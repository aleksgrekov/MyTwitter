from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from main import app
from src.database.config import settings
from src.database.models import Base, Follow, Tweet, User
from src.database.service import create_session
from tests.prepare_data import populate_database

TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db-dev"
engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
session_test = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, expire_on_commit=False
)


async def override_create_session():
    async with session_test() as session:
        yield session


app.dependency_overrides[create_session] = override_create_session


async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def teardown_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="class", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"
    await setup_db()
    yield
    await teardown_db()
    db_path = Path("test.db-dev")

    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope="class")
async def session():
    async with session_test() as session:
        yield session


@pytest.fixture(scope="class")
async def populate_database_fixture(session) -> None:
    await populate_database(session)


@pytest.fixture(scope="class")
async def users_and_followers(session):
    user1 = User(username="test_user1", name="Test User1")
    user2 = User(username="test_user2", name="Test User2")
    user3 = User(username="test_user3", name="Test User3")
    user4 = User(username="test_user4", name="Test User4")

    session.add_all([user1, user2, user3, user4])
    await session.flush()

    follow1 = Follow(follower_id=user1.id, following_id=user2.id)
    follow2 = Follow(follower_id=user2.id, following_id=user1.id)
    follow3 = Follow(follower_id=user1.id, following_id=user4.id)

    session.add_all([follow1, follow2, follow3])
    await session.commit()

    return user1, user2, user3, user4


@pytest.fixture(scope="class")
async def test_tweet(session, users_and_followers):
    tweet = Tweet(
        author_id=users_and_followers[0].id,
        tweet_data="Hello, world!",
    )
    session.add(tweet)
    await session.commit()
    await session.refresh(tweet)
    return tweet
