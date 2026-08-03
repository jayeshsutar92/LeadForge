"""Search history endpoints."""
from fastapi import APIRouter, Depends, Request

from services.auth_service import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def list_history(request: Request, user=Depends(get_current_user)):
    db = request.state.db
    docs = await db.search_history.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(length=50)
    return {"results": docs}


@router.delete("")
async def clear_history(request: Request, user=Depends(get_current_user)):
    db = request.state.db
    res = await db.search_history.delete_many({"user_id": user["id"]})
    return {"deleted": res.deleted_count}
