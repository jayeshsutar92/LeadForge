from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.api.deps import get_db_session
from app.core.redis import get_redis_client

router = APIRouter()


@router.get("/liveness", tags=["health"])
async def liveness() -> dict:
    """Liveness probe to check if the application is running."""
    return {"status": "ok"}


@router.get("/readiness", tags=["health"])
async def readiness(session: AsyncSession = Depends(get_db_session)) -> JSONResponse:
    """Readiness probe to check if all dependencies are accessible."""
    status = {"status": "ok", "database": "unknown", "redis": "unknown"}
    is_ready = True

    # Check Database
    try:
        await session.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        is_ready = False

    # Check Redis
    try:
        redis = get_redis_client()
        if await redis.ping():
            status["redis"] = "ok"
        else:
            status["redis"] = "error: ping failed"
            is_ready = False
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
        is_ready = False

    return JSONResponse(
        status_code=200 if is_ready else 503,
        content=status
    )
