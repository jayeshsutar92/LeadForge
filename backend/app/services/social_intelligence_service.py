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

    async def trigger_analysis(self, business_slug: str, user_id: UUID) -> SocialIntelligence:
        business = await self.business_repo.get_by_slug(business_slug, user_id)
        if not business:
            raise ValueError(f"Business not found: {business_slug}")
            
        # Only run if website is not present
        if business.website and business.website.strip():
            logger.info(f"Skipping social intelligence for {business.name} because website exists.")
            return None

        # Check if we already did it
        existing = await self.repo.get_by_business_id(business.id)
        if existing:
            return existing
            
        # Discover profiles
        try:
            data = await discover_social_profiles(
                business_name=business.name,
                category=business.category,
                city=business.city,
                country=business.country
            )
        except Exception as e:
            logger.error(f"Error discovering social profiles for {business.name}: {e}")
            raise e

        # Save to database
        si = await self.repo.create(business.id, data)
        return si
