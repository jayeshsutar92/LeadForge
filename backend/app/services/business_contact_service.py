from app.repositories.business_contact import BusinessContactRepository
from app.models.business_contact import BusinessContact
from uuid import UUID

class BusinessContactService:
    def __init__(self, session) -> None:
        self.session = session
        self.repo = BusinessContactRepository(session)

    async def get_contact(self, contact_id: UUID) -> BusinessContact | None:
        return await self.repo.get_by_id(contact_id)

    async def list_contacts(self, business_id: UUID, limit: int = 100) -> list[BusinessContact]:
        return await self.repo.list_by_business(business_id, limit=limit)

    async def create_contact(self, contact: BusinessContact) -> BusinessContact:
        return await self.repo.create(contact)

    async def update_contact(self, contact_id: UUID, **kwargs) -> BusinessContact | None:
        return await self.repo.update(contact_id, **kwargs)

    async def delete_contact(self, contact_id: UUID) -> int:
        return await self.repo.delete(contact_id)
