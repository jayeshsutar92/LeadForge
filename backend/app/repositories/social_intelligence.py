import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_intelligence import SocialIntelligence


class SocialIntelligenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, business_id: uuid.UUID, data: dict) -> SocialIntelligence:
        si = SocialIntelligence(
            business_id=business_id,
            data=data,
        )
        self.session.add(si)
        await self.session.commit()
        await self.session.refresh(si)
        return si

    async def get_by_business_id(self, business_id: uuid.UUID) -> Optional[SocialIntelligence]:
        stmt = (
            select(SocialIntelligence)
            .where(SocialIntelligence.business_id == business_id)
            .order_by(SocialIntelligence.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
