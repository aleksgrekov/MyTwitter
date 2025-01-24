from typing import List

from sqlalchemy import delete, exists, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow, Media, Tweet
from src.database.repositories.user_repository import get_user_id_by
from src.handlers.exceptions import (
    IntegrityViolationException,
    PermissionException,
    RowNotFoundException,
)
from src.schemas.base_schemas import SuccessSchema
from src.schemas.like_schemas import LikeSchema
from src.schemas.tweet_schemas import (
    NewTweetResponseSchema,
    TweetBaseSchema,
    TweetResponseSchema,
    TweetSchema,
)
from src.schemas.user_schemas import UserSchema


async def collect_tweet_data(tweet: "Tweet") -> TweetSchema:
    """
    Collect detailed tweet data including attachments and likes.

    This function retrieves detailed information about the tweet, including
    media attachments and associated likes.

    Args:
        tweet (Tweet): The tweet object containing the tweet data.

    Returns:
        TweetSchema: A schema containing detailed tweet information including
        content, attachments, author, and likes.
    """

    attachments = [media.link for media in tweet.media]
    author_data = UserSchema.model_validate(tweet.author)
    likes_data = [LikeSchema.model_validate(like) for like in tweet.likes]

    return TweetSchema(
        id=tweet.id,
        content=tweet.tweet_data,
        attachments=attachments,
        author=author_data,
        likes=likes_data,
    )


async def is_tweet_exist(tweet_id: int, session: AsyncSession) -> bool:
    """
    Check if a tweet exists by its ID.

    This function checks whether a tweet with the specified ID exists in the
    database.

    Args:
        tweet_id (int): The ID of the tweet to check.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        bool: True if the tweet exists, False otherwise.
    """
    query = select(exists().where(Tweet.id == tweet_id))
    response = await session.scalar(query)
    return response is not None and response


async def get_tweets_selection(
    username: str, session: AsyncSession
) -> TweetResponseSchema:
    """
    Get all tweets for a user.

    This function retrieves all tweets of a user and their followees.

    Args:
        username (str): The username of the user whose tweets are to be retrieved.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        TweetResponseSchema: A schema containing a list of tweets with detailed data.

    Raises:
        RowNotFoundException: If the user is not found in the database.
    """
    user_id = await get_user_id_by(username, session)
    if not user_id:
        raise RowNotFoundException()

    query = (
        select(Tweet)
        .join(Follow, Follow.following_id == Tweet.author_id)
        .where(Follow.follower_id == user_id)
    )
    tweets = (await session.scalars(query)).unique().all()

    tweet_schema = [await collect_tweet_data(tweet) for tweet in tweets]

    return TweetResponseSchema(tweets=tweet_schema)


async def add_tweet(
    username: str, tweet: TweetBaseSchema, session: AsyncSession
) -> NewTweetResponseSchema:
    """
    Add a new tweet.

    This function adds a new tweet by the user.

    Args:
        username (str): The username of the user who is posting the tweet.
        tweet (TweetBaseSchema): The tweet data to be added.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        NewTweetResponseSchema: A schema containing the ID of the newly created tweet.

    Raises:
        RowNotFoundException: If the user does not exist.
        IntegrityViolationException: If there is a database integrity error.
    """
    user_id = await get_user_id_by(username, session)
    if not user_id:
        raise RowNotFoundException()

    new_tweet = Tweet(author_id=user_id, tweet_data=tweet.tweet_data)
    session.add(new_tweet)
    try:
        await save_tweet_and_update_media(new_tweet, tweet.tweet_media_ids, session)
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))
    return NewTweetResponseSchema(tweet_id=new_tweet.id)


async def save_tweet_and_update_media(
    tweet: Tweet, media_ids: List[int], session: AsyncSession
) -> None:
    """
    Save the tweet and update media references in the database.

    Args:
        tweet (Tweet): The tweet for updating media.
        media_ids (list[int]): List of media IDs to be associated with the tweet.
        session (AsyncSession): The database session used for executing queries.

    Raises:
        IntegrityError: If there is a database integrity error.
    """
    await session.flush()
    if media_ids:
        query = update(Media).where(Media.id.in_(media_ids)).values(tweet_id=tweet.id)
        await session.execute(query)
    await session.commit()


async def delete_tweet(
    username: str, tweet_id: int, session: AsyncSession
) -> SuccessSchema:
    """
    Delete a tweet.

    This function deletes the tweet specified by `tweet_id` if the user is
    the author of the tweet.

    Args:
        username (str): The username of the user who is deleting the tweet.
        tweet_id (int): The ID of the tweet to be deleted.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        SuccessSchema: A schema indicating that the tweet was successfully deleted.

    Raises:
        RowNotFoundException: If the user does not exist.
        PermissionException: If the user is not authorized to delete the tweet.
        IntegrityViolationException: If there is a database integrity error.
    """
    user_id = await get_user_id_by(username, session)
    if not user_id:
        raise RowNotFoundException()

    query = (
        delete(Tweet)
        .returning(Tweet.id)
        .where(Tweet.id == tweet_id, Tweet.author_id == user_id)
    )
    request = await session.execute(query)
    if not request.fetchone():
        raise PermissionException(
            f"User with {username=} can't delete tweet with {tweet_id=}"
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return SuccessSchema()
