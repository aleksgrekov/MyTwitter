# import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.models import Base

# DATABASE_USER = os.getenv('DATABASE_USER')
# DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
# DATABASE_HOST = os.getenv('DATABASE_HOST')
# DATABASE_PORT = os.getenv('DATABASE_PORT')
# DATABASE_NAME = os.getenv('DATABASE_NAME')

DATABASE_USER = "admin"
DATABASE_PASSWORD = "admin"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5433"
DATABASE_NAME = "my_twitter"

DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
