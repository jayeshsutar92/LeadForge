from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from routers import auth as auth_router
from routers import businesses as businesses_router
from routers import search_history as history_router
from services.seed import seed_businesses
from services.auth_service import seed_admin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
db_name = os.environ.get("DB_NAME", "leadforge")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, client
    try:
        test_client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=3000)
        await test_client.admin.command('ping')
        client = test_client
        db = client[db_name]
        logger.info("Connected to MongoDB server at %s", mongo_url)
    except Exception as exc:
        logger.warning("Local MongoDB not available (%s). Using in-memory database fallback.", exc)
        from mongomock_motor import AsyncMongoMockClient
        client = AsyncMongoMockClient()
        db = client[db_name]

    # Indexes
    try:
        await db.users.create_index("email", unique=True)
        await db.login_attempts.create_index("identifier")
        await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
        await db.businesses.create_index("slug", unique=True)
        await db.businesses.create_index([("name", "text"), ("category", "text"), ("city", "text")])
        await db.search_history.create_index([("user_id", 1), ("created_at", -1)])
    except Exception:
        pass

    # Seed data
    await seed_admin(db)
    await seed_businesses(db)

    # Write test credentials for the QA agent
    try:
        creds_dir = Path("/app/memory")
        creds_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        creds_dir = ROOT_DIR / "memory"
        creds_dir.mkdir(parents=True, exist_ok=True)

    creds_file = creds_dir / "test_credentials.md"
    creds_file.write_text(
        "# Test Credentials\n\n"
        "## Admin Account\n"
        f"- Email: {os.environ.get('ADMIN_EMAIL', 'jayeshsutar76@gmail.com')}\n"
        f"- Password: {os.environ.get('ADMIN_PASSWORD', 'admin123')}\n"
        "- Role: admin\n\n"
        "## Auth Endpoints\n"
        "- POST /api/auth/register\n"
        "- POST /api/auth/login\n"
        "- POST /api/auth/logout\n"
        "- GET /api/auth/me\n"
    )

    yield
    if hasattr(client, "close"):
        client.close()


app = FastAPI(title="LeadForge API", lifespan=lifespan)


# Attach db to app state so routers can access
@app.middleware("http")
async def db_middleware(request, call_next):
    request.state.db = db
    return await call_next(request)


# CORS
allowed_origin = os.environ.get("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin] if allowed_origin != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router.router)
app.include_router(businesses_router.router)
app.include_router(history_router.router)


@app.get("/api")
async def api_root():
    return {"service": "LeadForge API", "status": "ok"}
