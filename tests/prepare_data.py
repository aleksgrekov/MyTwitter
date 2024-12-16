import random
from pathlib import Path

import aiofiles
from aiofiles.os import wrap
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from logger.logger_setup import get_logger
from database.models import User, Tweet, Like, Follow

NUM_USERS = 10
NUM_TWEETS = 20
NUM_LIKES = 30
NUM_FOLLOWS = 15

faker = Faker()
data_logger = get_logger(__name__)
path_exists = wrap(Path.exists)


async def clear_log_file(log_path: Path) -> None:
    """
    Asynchronously clears the log file.

    Args:
        log_path (Path): Path to the log file.
    """
    try:
        if await path_exists(log_path):
            async with aiofiles.open(log_path, 'w') as f:
                await f.write("")
            data_logger.debug("Log file cleared.")
    except Exception as e:
        data_logger.exception(f"Error while clearing the log file: {e}")
        raise


def generate_users(num_users: int = NUM_USERS) -> list[User]:
    """
    Generates a list of users.

    Args:
        num_users (int): Number of users to generate. Default is NUM_USERS.

    Returns:
        list[User]: List of User objects.
    """
    usernames = set()
    users = []
    while len(users) < num_users:
        username = faker.user_name()
        if username not in usernames:
            usernames.add(username)
            users.append(User(username=username, name=faker.name()))
    users.append(User(username="test", name="Test Name"))
    data_logger.debug(f"Created {len(users)} users.")
    return users


def generate_follows(user_ids: list[int], num_follows: int = NUM_FOLLOWS) -> list[Follow]:
    """
    Generates unique follows between users.

    Args:
        user_ids (list[int]): List of user IDs.
        num_follows (int): Number of follows to generate. Default is NUM_FOLLOWS.

    Returns:
        list[Follow]: List of Follow objects.
    """
    if len(user_ids) < 2:
        data_logger.warning("Not enough user IDs to generate follows.")
        return []

    follows = set()
    while len(follows) < num_follows:
        follower_id, followed_id = random.sample(user_ids, 2)
        follows.add((follower_id, followed_id))

    follows.add((11, 1))
    follow_objects = [Follow(follower_id=f, following_id=t) for f, t in follows]
    data_logger.debug(f"Created {len(follow_objects)} follows.")
    return follow_objects


def generate_tweets(user_ids: list[int], num_tweets: int = NUM_TWEETS) -> list[Tweet]:
    """
    Generates a list of tweets from random users.

    Args:
        user_ids (list[int]): List of user IDs.
        num_tweets (int): Number of tweets to generate. Default is NUM_TWEETS.

    Returns:
        list[Tweet]: List of Tweet objects.
    """
    if not user_ids:
        data_logger.warning("User IDs are empty, cannot generate tweets.")
        return []

    tweets = [
        Tweet(author_id=random.choice(user_ids), tweet_data=faker.sentence(), tweet_media_ids=[])
        for _ in range(num_tweets)
    ]
    tweets.append(
        Tweet(author_id=1, tweet_data=faker.sentence(), tweet_media_ids=[]))
    data_logger.debug(f"Created {len(tweets)} tweets.")
    return tweets


def generate_likes(user_ids: list[int], tweet_ids: list[int], num_likes: int = NUM_LIKES) -> list[Like]:
    """
    Generates likes from random users for random tweets.

    Args:
        user_ids (list[int]): List of user IDs.
        tweet_ids (list[int]): List of tweet IDs.
        num_likes (int): Number of likes to generate. Default is NUM_LIKES.

    Returns:
        list[Like]: List of Like objects.
    """
    if not user_ids or not tweet_ids:
        data_logger.warning("User IDs or Tweet IDs are empty, cannot generate likes.")
        return []

    likes = [
        Like(user_id=random.choice(user_ids), tweet_id=random.choice(tweet_ids))
        for _ in range(num_likes)
    ]
    data_logger.debug(f"Created {len(likes)} likes.")
    return likes


async def populate_database(session: AsyncSession) -> None:
    """
    Populates the database with test data.

    Steps:
    1. Clears the log file.
    2. Generates users.
    3. Generates follows.
    4. Generates tweets.
    5. Generates likes.

    Args:
        session (AsyncSession): Async SQLAlchemy session to interact with the database.
    """
    log_file_path = Path(__name__).parent / "logger/logfile.log"
    await clear_log_file(log_file_path)

    try:
        async with session.begin():
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

    except Exception as e:
        data_logger.exception(f"Error while populating the database: {e}")
        raise
