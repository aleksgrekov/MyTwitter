from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database.service import create_session, Base
from src.main import app
from .prepare_data import populate_database

TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost:5432/test"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=StaticPool)
session_test = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    expire_on_commit=False
)


async def override_get_db():
    async with session_test() as session:
        yield session


app.dependency_overrides[create_session] = override_get_db


async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def teardown_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module", autouse=True)
async def prepare_database():
    await setup_db()
    await populate_database(session=session_test())
    yield
    await teardown_db()


@pytest.fixture(scope="module")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac