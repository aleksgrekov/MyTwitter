import random

from faker import Faker
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Tweet, Media, Like, Follow

faker = Faker()


async def create_follow_if_not_exists(
        session: AsyncSession, follower_id: int, followed_id: int
) -> bool:
    if follower_id == followed_id:
        return False

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
        async with session.begin():
            session.add(User(username="test", name="Test Name"))
            await session.commit()

            users = [
                User(username=faker.user_name(), name=faker.name()) for _ in range(10)
            ]
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
