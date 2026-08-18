import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import build_redis_key, get_redis_client
from app.models.business_intelligence import BusinessIntelligence
from app.repositories.business import BusinessRepository
from app.repositories.business_intelligence import BusinessIntelligenceRepository
from app.services.analysis.deterministic import analyze_website
from app.core.config import get_settings
from app.agents.providers.factory import ProviderFactory
import logging

logger = logging.getLogger(__name__)

_BI_CACHE_TTL = 86400  # 24 hours


class BusinessIntelligenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = BusinessIntelligenceRepository(session)
        self.business_repo = BusinessRepository(session)
        self.redis = get_redis_client()

    def _cache_key(self, business_id: str) -> str:
        return build_redis_key("business_intelligence", business_id)

    async def get_latest(self, business_id: UUID, user_id: UUID | None = None) -> BusinessIntelligence | None:
        if user_id:
            business = await self.business_repo.get_by_id(business_id, user_id=user_id)
            if not business:
                raise HTTPException(status_code=403, detail="Not authorized to access this intelligence report")

        key = self._cache_key(str(business_id))
        cached = await self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                bi_id = data.get("id")
                if bi_id:
                    bi = await self.repo.get_by_id(UUID(bi_id))
                    if bi:
                        return bi
            except (json.JSONDecodeError, ValueError):
                pass
                
        bi = await self.repo.get_latest_by_business(business_id)
        if bi:
            await self._set_cache(key, bi)
        return bi

    async def _set_cache(self, key: str, bi: BusinessIntelligence) -> None:
        payload = json.dumps({"id": str(bi.id)})
        await self.redis.set(key, payload, ex=_BI_CACHE_TTL)

    async def trigger_analysis(self, business_slug: str, user_id: UUID) -> BusinessIntelligence:
        """Run deterministic analysis and save results."""
        business = await self.business_repo.get_by_slug(business_slug, user_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        # For businesses without websites, we just perform a basic analysis
        url = business.website or ""
        
        # Run deterministic analysis
        analysis_data = await analyze_website(url)
        
        # Override the title/summary with DB data to ensure it's not totally empty
        if not url:
            analysis_data["summary"] = f"{business.name} is a {business.category} business located in {business.city}, {business.country}."
            analysis_data["website_metadata"]["title"] = business.name
        else:
            # Use AI to generate a proper business analysis summary
            try:
                settings = get_settings()
                config = settings.model_dump()
                provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
                prompt = f"Analyze this website data and write a concise 2-sentence summary of what the business '{business.name}' does, its core offerings, and its target audience based on the following extracted data: {json.dumps(analysis_data['website_metadata'])}"
                
                ai_summary = await provider.generate(prompt=prompt)
                if ai_summary:
                    analysis_data["summary"] = ai_summary
            except Exception as e:
                logger.error(f"Failed to generate AI summary for BI: {e}")
                # Don't raise error, fallback to deterministic summary
                pass
            
        bi = await self.repo.create(business.id, analysis_data, analysis_type="deterministic")
        
        # Update cache
        key = self._cache_key(str(business.id))
        await self._set_cache(key, bi)
        
        return bi

    async def list_history(self, business_slug: str, limit: int = 10, offset: int = 0, user_id: UUID | None = None) -> list[BusinessIntelligence]:
        business = await self.business_repo.get_by_slug(business_slug, user_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        return await self.repo.list_by_business(business.id, limit=limit, offset=offset)

    async def count_history(self, business_slug: str, user_id: UUID | None = None) -> int:
        business = await self.business_repo.get_by_slug(business_slug, user_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        return await self.repo.count_by_business(business.id)
