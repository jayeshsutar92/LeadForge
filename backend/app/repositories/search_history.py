from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_history import SearchHistory


class SearchHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, history: SearchHistory) -> SearchHistory:
        self.session.add(history)
        await self.session.commit()
        await self.session.refresh(history)
        return history

    async def list_for_user(self, user_id: UUID, limit: int = 50) -> list[SearchHistory]:
        from sqlalchemy import select, desc
        statement = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(desc(SearchHistory.created_at))
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete_for_user(self, user_id: UUID) -> int:
        from sqlalchemy import delete
        statement = delete(SearchHistory).where(SearchHistory.user_id == user_id)
        result = await self.session.execute(statement)
        await self.session.commit()
        return result.rowcount
