from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.search_history import SearchHistoryRepository

router = APIRouter()


@router.get("")
async def list_history(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = SearchHistoryRepository(session)
    history = await repo.list_for_user(user.id, limit=50)
    
    docs = []
    for h in history:
        docs.append({
            "id": str(h.id),
            "user_id": str(h.user_id),
            "query": h.query,
            "filters": h.filters,
            "result_count": h.result_count,
            "created_at": h.created_at.isoformat(),
        })
        
    return {"results": docs}


@router.delete("")
async def clear_history(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = SearchHistoryRepository(session)
    deleted_count = await repo.delete_for_user(user.id)
    return {"deleted": deleted_count}
