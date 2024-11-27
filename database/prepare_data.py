import random
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Tweet, Media, Like, Follow

faker = Faker()


async def populate_database(session: AsyncSession):
    """Создает тестовые записи и добавляет их в базу данных."""

    users = [
        User(username=User.hash_username(faker.user_name()), name=faker.name())
        for _ in range(10)
    ]
    session.add_all(users)
    await session.flush()

    tweets = [
        Tweet(author_id=random.choice(users).id, content=faker.sentence())
        for _ in range(20)
    ]
    session.add_all(tweets)
    await session.flush()

    media = [
        Media(link=faker.image_url())
        for _ in range(5)
    ]
    session.add_all(media)

    likes = [
        Like(author_id=random.choice(users).id, tweet_id=random.choice(tweets).id)
        for _ in range(30)
    ]
    session.add_all(likes)

    follows = [
        Follow(
            follower_id=random.choice(users).id,
            followed_id=random.choice([u.id for u in users if u.id != users[0].id])
        )
        for _ in range(15)
    ]
    session.add_all(follows)

    await session.commit()
