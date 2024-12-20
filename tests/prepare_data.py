import random
from typing import List

from faker import Faker

from database.models import User, Follow, Tweet, Like
from logger.logger_setup import get_logger

NUM_USERS = 10
NUM_TWEETS = 20
NUM_LIKES = 30
NUM_FOLLOWS = 15

faker = Faker()
test_logger = get_logger(__name__)


def generate_users(num_users: int = NUM_USERS) -> List[User]:
    """
    Generates a list of users.

    Args:
        num_users (int): Number of users to generate. Default is NUM_USERS.

    Returns:
        List[User]: List of User objects.
    """
    usernames = set()
    users = []
    while len(users) < num_users:
        username = faker.user_name()
        if username not in usernames:
            usernames.add(username)
            users.append(User(username=username, name=faker.name()))
    users.append(User(username="test", name="Test Name"))
    test_logger.debug(f"Created {len(users)} users.")
    return users


def generate_follows(user_ids: List[int], num_follows: int = NUM_FOLLOWS) -> List[Follow]:
    """
    Generates unique follows between users.

    Args:
        user_ids (List[int]): List of user IDs.
        num_follows (int): Number of follows to generate. Default is NUM_FOLLOWS.

    Returns:
        List[Follow]: List of Follow objects.
    """
    if len(user_ids) < 2:
        test_logger.warning("Not enough user IDs to generate follows.")
        return []

    follows = set()
    while len(follows) < num_follows:
        follower_id, followed_id = random.sample(user_ids, 2)
        follows.add((follower_id, followed_id))

    follows.add((11, 1))
    follow_objects = [Follow(follower_id=f, following_id=t) for f, t in follows]
    test_logger.debug(f"Created {len(follow_objects)} follows.")
    return follow_objects


def generate_tweets(user_ids: List[int], num_tweets: int = NUM_TWEETS) -> List[Tweet]:
    """
    Generates a list of tweets from random users.

    Args:
        user_ids (List[int]): List of user IDs.
        num_tweets (int): Number of tweets to generate. Default is NUM_TWEETS.

    Returns:
        List[Tweet]: List of Tweet objects.
    """
    if not user_ids:
        test_logger.warning("User IDs are empty, cannot generate tweets.")
        return []

    tweets = [
        Tweet(author_id=random.choice(user_ids), tweet_data=faker.sentence(), tweet_media_ids=[])
        for _ in range(num_tweets)
    ]
    tweets.append(
        Tweet(author_id=1, tweet_data=faker.sentence(), tweet_media_ids=[]))
    test_logger.debug(f"Created {len(tweets)} tweets.")
    return tweets


def generate_likes(user_ids: List[int], tweet_ids: List[int], num_likes: int = NUM_LIKES) -> List[Like]:
    """
    Generates likes from random users for random tweets.

    Args:
        user_ids (List[int]): List of user IDs.
        tweet_ids (List[int]): List of tweet IDs.
        num_likes (int): Number of likes to generate. Default is NUM_LIKES.

    Returns:
        List[Like]: List of Like objects.
    """
    if not user_ids or not tweet_ids:
        test_logger.warning("User IDs or Tweet IDs are empty, cannot generate likes.")
        return []

    likes = [
        Like(user_id=random.choice(user_ids), tweet_id=random.choice(tweet_ids))
        for _ in range(num_likes)
    ]
    test_logger.debug(f"Created {len(likes)} likes.")
    return likes
