import random
from pathlib import Path

import aiofiles
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from logger.logger_setup import get_logger
from database.models import User, Tweet, Like, Follow

faker = Faker()
data_logger = get_logger(__name__)


async def clear_log_file(log_path: Path) -> None:
    """Асинхронно очищает файл логов."""
    try:
        if log_path.exists():
            async with aiofiles.open(log_path, 'w') as f:
                await f.write("")
            data_logger.debug("Лог файл очищен.")
    except Exception as e:
        data_logger.exception(f"Ошибка при очистке лог файла: {e}")


def generate_users(num_users: int = 10) -> list[User]:
    """Генерирует список пользователей."""
    users = [User(username=faker.user_name(), name=faker.name()) for _ in range(num_users)]
    users.append(User(username="test", name="Test Name"))
    data_logger.debug(f"Создано {len(users)} пользователей.")
    return users


def generate_follows(user_ids: list[int], num_follows: int = 15) -> list[Follow]:
    """Генерирует уникальные подписки."""
    follows = set()
    while len(follows) < num_follows:
        follower_id, followed_id = random.sample(user_ids, 2)
        follows.add((follower_id, followed_id))

    follows.add((11, 1))
    follow_objects = [Follow(follower_id=f, following_id=t) for f, t in follows]
    data_logger.debug(f"Создано {len(follow_objects)} подписок.")
    return follow_objects


def generate_tweets(user_ids: list[int], num_tweets: int = 20) -> list[Tweet]:
    """Генерирует твиты от случайных пользователей."""
    tweets = [
        Tweet(author_id=random.choice(user_ids), tweet_data=faker.sentence(), tweet_media_ids=[])
        for _ in range(num_tweets)
    ]
    tweets.append(Tweet(author_id=1, tweet_data=faker.sentence(), tweet_media_ids=[]))
    data_logger.debug(f"Создано {len(tweets)} твитов.")
    return tweets


def generate_likes(user_ids: list[int], tweet_ids: list[int], num_likes: int = 30) -> list[Like]:
    """Генерирует лайки от случайных пользователей к случайным твитам."""
    likes = [
        Like(user_id=random.choice(user_ids), tweet_id=random.choice(tweet_ids))
        for _ in range(num_likes)
    ]
    data_logger.debug(f"Создано {len(likes)} лайков.")
    return likes


async def populate_database(session: AsyncSession) -> None:
    """Заполняет базу данных тестовыми данными."""
    log_file_path = Path(__name__).parent / "logger/logfile.log"
    await clear_log_file(log_file_path)

    try:
        async with session.begin():
            # 1. Генерация пользователей
            users = generate_users()
            session.add_all(users)
            await session.flush()
            user_ids = [user.id for user in users]

            # 2. Генерация подписок
            follows = generate_follows(user_ids)
            session.add_all(follows)

            # 3. Генерация твитов
            tweets = generate_tweets(user_ids)
            session.add_all(tweets)
            await session.flush()
            tweet_ids = [tweet.id for tweet in tweets]

            # 4. Генерация лайков
            likes = generate_likes(user_ids, tweet_ids)
            session.add_all(likes)

    except Exception as e:
        data_logger.exception(f"Ошибка при заполнении БД: {e}")