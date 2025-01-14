import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.database.models import Base, Follow, Tweet, User
from src.database.service import create_session
from src.main import app
from src.prepare_data import populate_database

TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/test_db"
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
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


@pytest.fixture(scope="session")
async def prepare_database():
    await teardown_db()
    await setup_db()

    yield

    await teardown_db()


@pytest.fixture(scope="session")
async def populate_database_fixture(prepare_database) -> None:
    async with session_test() as session:
        await populate_database(session)


@pytest.fixture(scope="session")
def get_session_test():
    return session_test()


@pytest.fixture(scope="session")
async def users_and_followers(get_session_test):
    async with get_session_test as session:
        user1 = User(username="test_user1", name="Test User1")
        user2 = User(username="test_user2", name="Test User2")
        user3 = User(username="test_user3", name="Test User3")

        session.add_all([user1, user2, user3])
        await session.flush()

        follow1 = Follow(follower_id=user1.id, following_id=user2.id)
        follow2 = Follow(follower_id=user2.id, following_id=user1.id)

        session.add_all([follow1, follow2])
        await session.commit()

        return user1, user2, user3


@pytest.fixture(scope="class")
async def test_tweet(get_session_test, users_and_followers):
    async with get_session_test as session:
        tweet = Tweet(
            author_id=users_and_followers[0].id,
            tweet_data="Hello, world!",
            tweet_media_ids=[],
        )
        session.add(tweet)
        await session.commit()
        await session.refresh(tweet)

        return tweet
