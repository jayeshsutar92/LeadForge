from uuid import UUID

from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_intelligence import BusinessIntelligence


class BusinessIntelligenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, business_id: UUID, data: dict, analysis_type: str = "deterministic") -> BusinessIntelligence:
        bi = BusinessIntelligence(
            business_id=business_id,
            analysis_type=analysis_type,
            data=data,
        )
        self.session.add(bi)
        await self.session.commit()
        await self.session.refresh(bi)
        return bi

    async def get_by_id(self, bi_id: UUID) -> BusinessIntelligence | None:
        result = await self.session.execute(
            select(BusinessIntelligence).where(BusinessIntelligence.id == bi_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_by_business(self, business_id: UUID) -> BusinessIntelligence | None:
        result = await self.session.execute(
            select(BusinessIntelligence)
            .where(BusinessIntelligence.business_id == business_id)
            .order_by(desc(BusinessIntelligence.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_business(self, business_id: UUID, limit: int = 60, offset: int = 0) -> list[BusinessIntelligence]:
        result = await self.session.execute(
            select(BusinessIntelligence)
            .where(BusinessIntelligence.business_id == business_id)
            .order_by(desc(BusinessIntelligence.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_business(self, business_id: UUID) -> int:
        result = await self.session.execute(
            select(BusinessIntelligence).where(BusinessIntelligence.business_id == business_id)
        )
        return len(result.scalars().all())

    async def delete(self, bi_id: UUID) -> int:
        result = await self.session.execute(delete(BusinessIntelligence).where(BusinessIntelligence.id == bi_id))
        await self.session.commit()
        return result.rowcount
