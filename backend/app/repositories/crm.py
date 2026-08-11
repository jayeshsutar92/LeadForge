from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lead import Lead, Activity


class CRMRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ─── Lead Operations ────────────────────────────────────────────────────────

    async def get_lead(self, lead_id: UUID, user_id: UUID) -> Lead | None:
        stmt = (
            select(Lead)
            .options(selectinload(Lead.activities))
            .where(Lead.id == lead_id, Lead.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_lead_by_business(self, business_id: UUID, user_id: UUID) -> Lead | None:
        stmt = (
            select(Lead)
            .options(selectinload(Lead.activities))
            .where(Lead.business_id == business_id, Lead.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_lead(self, lead: Lead) -> Lead:
        self.session.add(lead)
        await self.session.flush()
        await self.session.refresh(lead)
        return lead

    async def update_lead(self, lead_id: UUID, user_id: UUID, **kwargs) -> Lead | None:
        lead = await self.get_lead(lead_id, user_id)
        if not lead:
            return None
        
        for key, value in kwargs.items():
            setattr(lead, key, value)
            
        await self.session.flush()
        await self.session.refresh(lead)
        return lead

    async def delete_lead(self, lead_id: UUID, user_id: UUID) -> bool:
        lead = await self.get_lead(lead_id, user_id)
        if not lead:
            return False
        await self.session.delete(lead)
        await self.session.flush()
        return True

    async def list_leads(
        self,
        user_id: UUID,
        q: str | None = None,
        status: str | None = None,
        assigned_to: UUID | None = None,
        min_priority: int | None = None,
        limit: int = 50,
        offset: int = 0,
        sort: str = "created_desc",
    ) -> tuple[int, Sequence[Lead]]:
        stmt = select(Lead).where(Lead.user_id == user_id)
        count_stmt = select(func.count()).select_from(Lead).where(Lead.user_id == user_id)

        # Filters
        if q:
            # We could join business table to search by business name, but for now just notes
            search = f"%{q}%"
            filter_expr = or_(Lead.notes.ilike(search), Lead.source.ilike(search))
            stmt = stmt.where(filter_expr)
            count_stmt = count_stmt.where(filter_expr)
            
        if status:
            stmt = stmt.where(Lead.status == status)
            count_stmt = count_stmt.where(Lead.status == status)
            
        if assigned_to:
            stmt = stmt.where(Lead.assigned_to == assigned_to)
            count_stmt = count_stmt.where(Lead.assigned_to == assigned_to)
            
        if min_priority is not None:
            # 1 is high, 3 is low. min_priority=1 means only priority 1.
            stmt = stmt.where(Lead.priority <= min_priority)
            count_stmt = count_stmt.where(Lead.priority <= min_priority)

        # Sorting
        if sort == "priority_asc":
            stmt = stmt.order_by(Lead.priority.asc(), Lead.created_at.desc())
        elif sort == "priority_desc":
            stmt = stmt.order_by(Lead.priority.desc(), Lead.created_at.desc())
        elif sort == "next_follow_up":
            stmt = stmt.order_by(Lead.next_follow_up.asc().nulls_last())
        elif sort == "status":
            stmt = stmt.order_by(Lead.status.asc(), Lead.created_at.desc())
        else:
            stmt = stmt.order_by(Lead.created_at.desc())

        # Pagination
        stmt = stmt.limit(limit).offset(offset)

        total = await self.session.scalar(count_stmt) or 0
        result = await self.session.execute(stmt)
        return total, result.scalars().all()

    # ─── Activity Operations ────────────────────────────────────────────────────

    async def create_activity(self, activity: Activity) -> Activity:
        self.session.add(activity)
        await self.session.flush()
        await self.session.refresh(activity)
        return activity
