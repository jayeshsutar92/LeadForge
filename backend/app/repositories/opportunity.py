from uuid import UUID

from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity


class OpportunityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, business_intelligence_id: UUID, data: dict) -> Opportunity:
        opp = Opportunity(
            business_intelligence_id=business_intelligence_id,
            data=data,
        )
        self.session.add(opp)
        await self.session.commit()
        await self.session.refresh(opp)
        return opp

    async def get_by_id(self, opportunity_id: UUID) -> Opportunity | None:
        result = await self.session.execute(
            select(Opportunity).where(Opportunity.id == opportunity_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_by_business_intelligence(self, business_intelligence_id: UUID) -> Opportunity | None:
        result = await self.session.execute(
            select(Opportunity)
            .where(Opportunity.business_intelligence_id == business_intelligence_id)
            .order_by(desc(Opportunity.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_business_intelligence(self, business_intelligence_id: UUID, limit: int = 60, offset: int = 0) -> list[Opportunity]:
        result = await self.session.execute(
            select(Opportunity)
            .where(Opportunity.business_intelligence_id == business_intelligence_id)
            .order_by(desc(Opportunity.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, opportunity_id: UUID) -> int:
        result = await self.session.execute(delete(Opportunity).where(Opportunity.id == opportunity_id))
        await self.session.commit()
        return result.rowcount
