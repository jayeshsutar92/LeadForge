from fastapi import APIRouter

from app.api.v1.endpoints import auth, businesses, search_history

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(search_history.router, prefix="/history", tags=["history"])
