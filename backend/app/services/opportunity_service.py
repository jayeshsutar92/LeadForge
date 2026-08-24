import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import build_redis_key, get_redis_client
from app.models.opportunity import Opportunity
from app.repositories.business import BusinessRepository
from app.repositories.business_intelligence import BusinessIntelligenceRepository
from app.repositories.opportunity import OpportunityRepository
from app.services.analysis.opportunity_scorer import generate_opportunity

_OPP_CACHE_TTL = 86400  # 24 hours


class OpportunityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OpportunityRepository(session)
        self.bi_repo = BusinessIntelligenceRepository(session)
        self.business_repo = BusinessRepository(session)
        self.redis = get_redis_client()

    def _cache_key(self, bi_id: str) -> str:
        return build_redis_key("opportunity", bi_id)

    async def get_latest(self, bi_id: UUID, user_id: UUID | None = None) -> Opportunity | None:
        if user_id:
            bi = await self.bi_repo.get_by_id(bi_id)
            if bi:
                business = await self.business_repo.get_by_id(bi.business_id, user_id=user_id)
                if not business:
                    raise HTTPException(status_code=403, detail="Not authorized to access this opportunity")

        key = self._cache_key(str(bi_id))
        cached = await self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                opp_id = data.get("id")
                if opp_id:
                    opp = await self.repo.get_by_id(UUID(opp_id))
                    if opp:
                        return opp
            except (json.JSONDecodeError, ValueError):
                pass
                
        opp = await self.repo.get_latest_by_business_intelligence(bi_id)
        if opp:
            await self._set_cache(key, opp)
        return opp

    async def _set_cache(self, key: str, opp: Opportunity) -> None:
        payload = json.dumps({"id": str(opp.id)})
        await self.redis.set(key, payload, ex=_OPP_CACHE_TTL)

    async def generate_opportunity(self, bi_id: UUID, business_slug: str, user_id: UUID | None = None) -> Opportunity:
        """Run deterministic scoring and generate opportunity based on BI data."""
        business = await self.business_repo.get_by_slug(business_slug, user_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        bi = await self.bi_repo.get_by_id(bi_id)
        if not bi:
            raise HTTPException(status_code=404, detail="Business Intelligence record not found")
            
        if bi.business_id != business.id:
            raise HTTPException(status_code=400, detail="Business Intelligence record does not belong to this business")
            
        # Idempotency check: see if we already have an opportunity for this BI record
        existing_opp = await self.repo.get_latest_by_business_intelligence(bi.id)
        if existing_opp:
            return existing_opp
            
        import asyncio
        lock_key = f"lock:opportunity_generate:{bi.id}"
        is_locked = await self.redis.set(lock_key, "1", nx=True, ex=60)
        
        if not is_locked:
            for _ in range(10):
                await asyncio.sleep(2)
                existing_opp = await self.repo.get_latest_by_business_intelligence(bi.id)
                if existing_opp:
                    return existing_opp
            raise HTTPException(status_code=409, detail="Generation in progress, please wait.")
            
        try:
            # Run AI opportunity generation
            opp_data = await generate_opportunity(bi.data, business.name)
            
            opp = await self.repo.create(bi.id, opp_data)
            
            # Update cache
            key = self._cache_key(str(bi.id))
            await self._set_cache(key, opp)
            
            return opp
        finally:
            await self.redis.delete(lock_key)

    async def list_by_bi(self, bi_id: UUID, limit: int = 10, offset: int = 0) -> list[Opportunity]:
        return await self.repo.list_by_business_intelligence(bi_id, limit=limit, offset=offset)
