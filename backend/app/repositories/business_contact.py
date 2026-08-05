from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_contact import BusinessContact


class BusinessContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, contact_id: UUID) -> BusinessContact | None:
        result = await self.session.execute(select(BusinessContact).where(BusinessContact.id == contact_id))
        return result.scalar_one_or_none()

    async def list_by_business(self, business_id: UUID, limit: int = 100) -> list[BusinessContact]:
        result = await self.session.execute(
            select(BusinessContact)
            .where(BusinessContact.business_id == business_id)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, contact: BusinessContact) -> BusinessContact:
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def update(self, contact_id: UUID, **kwargs) -> BusinessContact | None:
        await self.session.execute(
            update(BusinessContact)
            .where(BusinessContact.id == contact_id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(contact_id)

    async def delete(self, contact_id: UUID) -> int:
        result = await self.session.execute(delete(BusinessContact).where(BusinessContact.id == contact_id))
        await self.session.commit()
        return result.rowcount
