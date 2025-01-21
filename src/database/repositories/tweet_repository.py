from sqlalchemy import delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow, Tweet
from src.database.repositories.media_repository import get_media_link_by
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


async def collect_tweet_data(tweet: "Tweet", session: AsyncSession) -> TweetSchema:
    """Collect detailed tweet data including attachments and likes."""
    attachments = [
        await get_media_link_by(media_id, session) for media_id in tweet.tweet_media_ids
    ]
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
    """Check if a tweet exists by its ID."""
    query = select(exists().where(Tweet.id == tweet_id))
    response = await session.scalar(query)
    return response is not None and response


async def get_tweets_selection(
    username: str, session: AsyncSession
) -> TweetResponseSchema:
    """Get all tweets for a user."""

    user_id = await get_user_id_by(username, session)
    if not user_id:
        raise RowNotFoundException()

    query = (
        select(Tweet)
        .join(Follow, Follow.following_id == Tweet.author_id)
        .where(Follow.follower_id == user_id)
    )
    tweets = (await session.scalars(query)).unique().all()

    tweet_schema = [await collect_tweet_data(tweet, session) for tweet in tweets]

    return TweetResponseSchema(tweets=tweet_schema)


async def add_tweet(
    username: str, tweet: TweetBaseSchema, session: AsyncSession
) -> NewTweetResponseSchema:
    """Add a new tweet."""
    user_id = await get_user_id_by(username, session)
    if not user_id:
        raise RowNotFoundException()

    new_tweet = Tweet(author_id=user_id, **tweet.model_dump())
    session.add(new_tweet)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))
    return NewTweetResponseSchema(tweet_id=new_tweet.id)


async def delete_tweet(
    username: str, tweet_id: int, session: AsyncSession
) -> SuccessSchema:
    """Delete a tweet."""
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
