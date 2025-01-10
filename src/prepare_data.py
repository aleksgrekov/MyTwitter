import random
from typing import List
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger_setup import get_logger
from src.database.models import User, Follow, Tweet, Like

faker = Faker()
prepare_data_logger = get_logger(__name__)

NUM_USERS = 10
NUM_TWEETS = 20
NUM_LIKES = 30
NUM_FOLLOWS = 15


def generate_users(num_users: int = NUM_USERS) -> List[User]:
    """
    Generates a list of users, ensuring unique usernames.
    """
    users = dict()
    for _ in range(num_users):
        first_name = faker.first_name()
        last_name = faker.unique.last_name()

        username = "{}{}".format(first_name.lower()[:1], last_name.lower())
        name = "{} {}".format(first_name, last_name)
        users[username] = name
    users["test"] = "Test User"

    prepare_data_logger.info(f"Created {len(users)} users.")
    return [User(username=u, name=n) for u, n in users.items()]


def generate_follows(user_ids: List[int], num_follows: int = NUM_FOLLOWS) -> List[Follow]:
    """
    Generates unique follows between users.
    """
    test_user_id = NUM_USERS + 1

    follows = set()
    while len(follows) < num_follows:
        pair = tuple(random.sample(user_ids, 2))
        if pair == (test_user_id, 1):
            continue
        follows.add(pair)
    follows.add((test_user_id, 2))

    prepare_data_logger.info(f"Created {len(follows)} follows.")
    return [Follow(follower_id=follower, following_id=following) for follower, following in follows]


def generate_tweets(user_ids: List[int], num_tweets: int = NUM_TWEETS) -> List[Tweet]:
    """
    Generates tweets from random users.
    """

    tweets = [
        Tweet(author_id=random.choice(user_ids), tweet_data=faker.sentence(), tweet_media_ids=[])
        for _ in range(num_tweets)
    ]
    tweets.append(Tweet(author_id=2, tweet_data=faker.sentence(), tweet_media_ids=[]))
    prepare_data_logger.info(f"Created {len(tweets)} tweets.")
    return tweets


def generate_likes(user_ids: List[int], tweet_ids: List[int], num_likes: int = NUM_LIKES) -> List[Like]:
    """
    Generates likes from random users for random tweets.
    """
    likes = set()
    while len(likes) < num_likes:
        pair = (random.choice(user_ids), random.choice(tweet_ids))
        likes.add(pair)

    prepare_data_logger.info(f"Created {len(likes)} likes.")
    return [Like(user_id=u, tweet_id=t) for u, t in likes]


async def populate_database(session: AsyncSession) -> None:
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
        prepare_data_logger.exception(f"Error while populating the database: {e}")
        raise
