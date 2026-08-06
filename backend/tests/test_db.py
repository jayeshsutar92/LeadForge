import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.base_class import Base

# Simple in-memory SQLite for testing models
@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def db_session_factory(db_engine):
    return async_sessionmaker(bind=db_engine, expire_on_commit=False)

@pytest.mark.asyncio
async def test_db_connection(db_engine):
    async with db_engine.connect() as conn:
        assert conn is not None
