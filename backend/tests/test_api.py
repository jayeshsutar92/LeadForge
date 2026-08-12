import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

def test_security_headers():
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
            response = await ac.get("/api")
            assert response.status_code == 200
            assert response.headers.get("x-content-type-options") == "nosniff"
            assert response.headers.get("x-frame-options") == "DENY"
            assert response.headers.get("x-xss-protection") == "1; mode=block"
    asyncio.run(_run())

def test_health_endpoints():
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
            response = await ac.get("/api/health/liveness")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
    asyncio.run(_run())

