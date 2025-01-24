from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.config import settings

DB_URL = settings.get_db_url
engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
