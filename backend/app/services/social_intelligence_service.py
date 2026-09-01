import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.business import BusinessRepository
from app.repositories.social_intelligence import SocialIntelligenceRepository
from app.services.analysis.social_intelligence_agent import discover_social_profiles
from app.models.social_intelligence import SocialIntelligence

logger = logging.getLogger(__name__)

class SocialIntelligenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SocialIntelligenceRepository(session)
        self.business_repo = BusinessRepository(session)

    async def trigger_analysis(self, business_slug: str, user_id: UUID, force: bool = False) -> SocialIntelligence:
        business = await self.business_repo.get_by_slug(business_slug, user_id)
        if not business:
            raise ValueError(f"Business not found: {business_slug}")
            
        # Only run if website is not present and it's not a forced refresh
        if not force and business.website and business.website.strip():
            logger.info(f"Skipping social intelligence for {business.name} because website exists.")
            return None

        from app.core.redis import get_redis_client
        redis_client = get_redis_client()
        lock_key = f"lock:social_intelligence:{business.id}"
        
        try:
            async with redis_client.lock(lock_key, timeout=120, blocking_timeout=10):
                # Check if we already did it
                existing = await self.repo.get_by_business_id(business.id)
                if not force and existing:
                    logger.info(f"[Social Intelligence] Returning cached data for {business.name} (Cache Hit)")
                    return existing
                    
                logger.info(f"[Social Intelligence] Starting analysis for {business.name} (Cache Miss / Force Refresh)")
                    
                # Discover profiles
                try:
                    data = await discover_social_profiles(
                        business_name=business.name,
                        category=business.category,
                        city=business.city,
                        country=business.country,
                        address=business.bio,
                        phone=business.phone or "",
                        website=business.website or ""
                    )
                except Exception as e:
                    logger.error(f"[Social Intelligence] External search or AI failure for {business.name}: {e}")
                    # Preserve existing if failure happens
                    if existing:
                        logger.info(f"[Social Intelligence] Preserving previous verified profiles for {business.name} due to failure.")
                        return existing
                    raise e

                # Prevent stale/low-confidence results from overriding existing verified data
                if existing and existing.data:
                    current_profiles = data.get("profiles", [])
                    old_profiles = existing.data.get("profiles", [])
                    
                    has_new_verified = any(p.get("status") == "Verified" for p in current_profiles)
                    has_old_verified = any(p.get("status") == "Verified" for p in old_profiles)
                    
                    if has_old_verified and not has_new_verified:
                        logger.warning(f"[Social Intelligence] New analysis found no verified profiles, preserving previous verified profiles for {business.name}.")
                        data["profiles"] = old_profiles
                        data["recommended_platform"] = existing.data.get("recommended_platform")
                        
                    # Also preserve old generated messages if the new run failed to generate them
                    if not data.get("messages") and existing.data.get("messages"):
                        logger.warning(f"[Social Intelligence] Preserving previous AI outreach messages for {business.name}.")
                        data["messages"] = existing.data.get("messages")

                if existing:
                    # Update existing record
                    logger.info(f"[Social Intelligence] Updating existing record for {business.name}")
                    existing.data = data
                    await self.session.commit()
                    await self.session.refresh(existing)
                    return existing
                else:
                    # Save to database
                    logger.info(f"[Social Intelligence] Creating new record for {business.name}")
                    si = await self.repo.create(business.id, data)
                    return si
        except Exception as lock_err:
            logger.error(f"[Social Intelligence] Lock acquisition failed or internal error for {business.name}: {lock_err}")
            # Fallback to existing if available
            existing = await self.repo.get_by_business_id(business.id)
            if existing:
                return existing
            raise lock_err
