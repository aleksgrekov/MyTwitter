from sqlalchemy import delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Like
from src.database.repositories.tweet_repository import is_tweet_exist
from src.database.repositories.user_repository import get_user_id_by
from src.handlers.exceptions import (
    IntegrityViolationException,
    RowAlreadyExists,
    RowNotFoundException,
)
from src.schemas.base_schemas import SuccessSchema


async def validate_user_and_tweet(
    username: str, tweet_id: int, session: AsyncSession
) -> int:
    """Validate that user and tweet exist. Return user ID."""
    user_id = await get_user_id_by(username, session)
    if not user_id:
        raise RowNotFoundException()
    elif not await is_tweet_exist(tweet_id, session):
        raise RowNotFoundException("Tweet with this ID does not exist")

    return user_id


async def is_like_exist(user_id: int, tweet_id: int, session: AsyncSession) -> bool:
    """Check if a like exists for a tweet by a user."""
    subquery = exists().where(Like.user_id == user_id, Like.tweet_id == tweet_id)
    query = select(subquery)
    response = await session.scalar(query)
    return response is not None and response


async def add_like(
    username: str, tweet_id: int, session: AsyncSession
) -> SuccessSchema:
    """Add a like for a tweet."""
    user_id = await validate_user_and_tweet(username, tweet_id, session)

    if await is_like_exist(user_id, tweet_id, session):
        raise RowAlreadyExists()

    session.add(Like(user_id=user_id, tweet_id=tweet_id))

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return SuccessSchema()


async def delete_like(
    username: str, tweet_id: int, session: AsyncSession
) -> SuccessSchema:
    """Remove a like from a tweet."""
    user_id = await validate_user_and_tweet(username, tweet_id, session)

    query = (
        delete(Like)
        .returning(Like.id)
        .where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )
    request = await session.execute(query)

    if not request.fetchone():
        raise RowNotFoundException("No like entry found for this user and tweet")

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return SuccessSchema()
