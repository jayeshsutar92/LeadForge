from uuid import UUID

from sqlalchemy import select, delete, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.proposal import Proposal


class ProposalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, opportunity_id: UUID, version: int, content: dict) -> Proposal:
        proposal = Proposal(
            opportunity_id=opportunity_id,
            version=version,
            content=content,
        )
        self.session.add(proposal)
        await self.session.commit()
        await self.session.refresh(proposal)
        return proposal

    async def update(self, proposal: Proposal, content: dict) -> Proposal:
        proposal.content = content
        await self.session.commit()
        await self.session.refresh(proposal)
        return proposal

    async def get_by_id(self, proposal_id: UUID) -> Proposal | None:
        result = await self.session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_by_opportunity(self, opportunity_id: UUID) -> Proposal | None:
        result = await self.session.execute(
            select(Proposal)
            .where(Proposal.opportunity_id == opportunity_id)
            .order_by(desc(Proposal.version))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_opportunity(self, opportunity_id: UUID, limit: int = 60, offset: int = 0) -> list[Proposal]:
        result = await self.session.execute(
            select(Proposal)
            .where(Proposal.opportunity_id == opportunity_id)
            .order_by(desc(Proposal.version))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_opportunity(self, opportunity_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Proposal).where(Proposal.opportunity_id == opportunity_id)
        )
        return result.scalar() or 0

    async def delete(self, proposal_id: UUID) -> int:
        result = await self.session.execute(delete(Proposal).where(Proposal.id == proposal_id))
        await self.session.commit()
        return result.rowcount
