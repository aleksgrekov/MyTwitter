import os
import tempfile

import pytest

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from src.database.models import Base
from src.database.service import create_session
from src.main import app
from tests.prepare_data import generate_users, generate_follows, generate_tweets, generate_likes, test_logger

TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/test_db"
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
session_test = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    expire_on_commit=False
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


@pytest.fixture(scope="session")
async def prepare_database():
    await setup_db()

    yield

    await teardown_db()


@pytest.fixture(scope="session", autouse=True)
async def populate_database(prepare_database) -> None:
    """
    Populates the database with test data.

    Steps:
    1. Generates users.
    2. Generates follows.
    3. Generates tweets.
    4. Generates likes.
    """
    async with session_test() as session:
        try:
            # 1. Generate users
            users = generate_users()
            session.add_all(users)
            await session.flush()
            user_ids = [user.id for user in users]

            # 2. Generate follows
            follows = generate_follows(user_ids)
            session.add_all(follows)

            # 3. Generate tweets
            tweets = generate_tweets(user_ids)
            session.add_all(tweets)
            await session.flush()
            tweet_ids = [tweet.id for tweet in tweets]

            # 4. Generate likes
            likes = generate_likes(user_ids, tweet_ids)
            session.add_all(likes)
            await session.commit()

        except Exception as e:
            test_logger.exception(f"Error while populating the database: {e}")
            raise


@pytest.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def api_key():
    return {"api-key": "test"}


@pytest.fixture
async def add_tweet(ac, api_key):
    tweet_data = {
        "tweet_data": "Test tweet"
    }
    response = await ac.post(
        "/api/tweets",
        json=tweet_data,
        headers=api_key
    )
    return response


@pytest.fixture
def temp_image():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
        f.write(b'fakeimagecontent')
        yield f.name
        os.remove(f.name)
