from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.discovery_session import DiscoverySession

class DiscoverySessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_session(self, user_id: uuid.UUID) -> DiscoverySession | None:
        stmt = (
            select(DiscoverySession)
            .where(DiscoverySession.user_id == user_id, DiscoverySession.is_active == True)
            .order_by(DiscoverySession.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
