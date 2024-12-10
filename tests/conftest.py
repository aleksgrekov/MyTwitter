from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from scr.main import app
from database.service import Model, create_session
from tests.prepare_data import populate_database

TEST_DATABASE_URL = "postgresql://admin:admin@localhost:5432/test"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=StaticPool)
session_test = async_sessionmaker(
    bind=engine_test,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

async def override_create_session():
    async with session_test() as session:
        yield session

async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def teardown_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

app.dependency_overrides[create_session] = override_create_session

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