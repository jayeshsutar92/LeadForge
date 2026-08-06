from fastapi import APIRouter, Depends

from app.api.deps import enforce_rate_limit
from app.api.v1.endpoints import agents, auth, businesses, health, search_history

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])

# Apply rate limiting to all business endpoints
protected_router = APIRouter(dependencies=[Depends(enforce_rate_limit)])
protected_router.include_router(auth.router, prefix="/auth", tags=["auth"])
protected_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
protected_router.include_router(search_history.router, prefix="/history", tags=["history"])
protected_router.include_router(agents.router, prefix="/agents", tags=["agents"])

api_router.include_router(protected_router)
