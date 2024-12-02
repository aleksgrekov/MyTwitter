import random

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from logger.logger_setup import get_logger

from .models import User, Tweet, Media, Like, Follow

faker = Faker()
data_logger = get_logger(__name__)


async def populate_database(session: AsyncSession):
    try:
        async with session.begin():

            # Создание пользователей
            users = [User(username=faker.user_name(), name=faker.name()) for _ in range(10)] + [
                User(username="test", name="Test Name")
            ]
            session.add_all(users)
            await session.flush()
            data_logger.debug("Пользователи добавлены")

            # Создание твитов
            tweets = [
                Tweet(author_id=random.choice(users).id, tweet_data=faker.sentence(), tweet_media_ids={})
                for _ in range(20)
            ]
            session.add_all(tweets)
            await session.flush()
            data_logger.debug("Твиты добавлены")

            # Создание медиа
            session.add_all([Media(link=faker.image_url()) for _ in range(5)])
            data_logger.debug("Медиа добавлены")

            # Создание лайков
            session.add_all([
                Like(author_id=random.choice(users).id, tweet_id=random.choice(tweets).id)
                for _ in range(30)
            ])
            data_logger.debug("Лайки добавлены")

            # Создание подписок
            follows = set()
            while len(follows) < 15:
                follower_id, followed_id = random.sample([user.id for user in users], 2)
                follows.add((follower_id, followed_id))

            session.add_all([Follow(follower_id=f, following_id=t) for f, t in follows])
            data_logger.debug("Подписки добавлены")

    except Exception as e:
        await session.rollback()
        data_logger.exception("{} {}".format(e.__class__.__name__, e))
