import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Avoid logging health checks to prevent spam
        if request.url.path in ["/health/liveness", "/health/readiness", "/api/health/liveness", "/api/health/readiness"]:
            return await call_next(request)

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                f"{request.method} {request.url.path} {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} 500",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise
