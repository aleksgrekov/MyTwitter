import asyncio
import random
from pathlib import Path
from typing import List, Literal

import aiofiles
from faker import Faker
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Tweet, Media, Like, Follow

faker = Faker()
file_lock = asyncio.Lock()
file_path = Path(__file__).parent / "users.txt"


async def manage_file(mode: Literal["w", "a"], content: str = "") -> None:
    global file_lock, file_path
    async with file_lock:
        async with aiofiles.open(file_path, mode=mode) as file:
            if mode == "w":
                await file.write("")
            elif mode == "a":
                await file.write(content + "\n")


async def generate_users(count: int) -> List[User]:
    users = [
        User(username=faker.user_name(), name=faker.name()) for _ in range(count)
    ]
    users.append(User(username="test", name="Test Name"))

    for user in users:
        user_data = f"{user.name}:{user.username}"
        await manage_file("a", user_data)

    return users


async def create_follow_if_not_exists(
        session: AsyncSession, follower_id: int, followed_id: int
) -> bool:
    if follower_id == followed_id:
        return False  # Пользователь не может подписаться сам на себя

    query = select(exists().where(
        Follow.follower_id == follower_id,
        Follow.following_id == followed_id
    ))
    result = await session.execute(query)
    exists_in_db = result.scalar()

    if not exists_in_db:
        session.add(Follow(follower_id=follower_id, following_id=followed_id))
        return True
    return False


async def populate_database(session: AsyncSession):
    try:
        await manage_file("w")

        async with session.begin():
            users = await generate_users(10)
            session.add_all(users)
            await session.flush()

            tweets = [
                Tweet(author_id=random.choice(users).id, tweet_data=faker.sentence(), tweet_media_ids=dict())
                for _ in range(20)
            ]
            session.add_all(tweets)
            await session.flush()

            media = [Media(link=faker.image_url()) for _ in range(5)]
            session.add_all(media)

            likes = [
                Like(author_id=random.choice(users).id, tweet_id=random.choice(tweets).id)
                for _ in range(30)
            ]
            session.add_all(likes)

            follows_count = 15
            follows_created = 0
            while follows_created < follows_count:
                follower_id = random.choice(users).id
                followed_id = random.choice([u for u in users if u.id != follower_id]).id

                if await create_follow_if_not_exists(session, follower_id, followed_id):
                    follows_created += 1
            else:
                await session.commit()
    except Exception as e:
        await session.rollback()
        print(e.__class__.__name__, e)
