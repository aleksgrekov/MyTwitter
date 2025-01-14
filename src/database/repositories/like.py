from typing import Union

from sqlalchemy import delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Like
from src.database.repositories.tweet import is_tweet_exist
from src.database.repositories.user import get_user_id_by
from src.database.schemas.base import ErrorResponseSchema, SuccessSchema
from src.functions import exception_handler
from src.logger_setup import get_logger

like_rep_logger = get_logger(__name__)


async def is_like_exist(user_id: int, tweet_id: int, session: AsyncSession) -> bool:
    """Check if a like exists for a tweet by a user."""
    return await session.scalar(
        select(exists().where(Like.user_id == user_id, Like.tweet_id == tweet_id))
    )


async def add_like(
    username: str, tweet_id: int, session: AsyncSession
) -> Union[SuccessSchema, ErrorResponseSchema]:
    """Add a like for a tweet."""
    user_id = await get_user_id_by(username, session)

    if not user_id:
        return exception_handler(
            like_rep_logger,
            ValueError.__class__.__name__,
            "User with this username does not exist",
        )

    elif not await is_tweet_exist(tweet_id, session):
        return exception_handler(
            like_rep_logger,
            ValueError.__class__.__name__,
            "Tweet with this tweet_id does not exist",
        )
    elif await is_like_exist(user_id, tweet_id, session):
        return exception_handler(
            like_rep_logger, ValueError.__class__.__name__, "Like already exists"
        )

    session.add(Like(user_id=user_id, tweet_id=tweet_id))

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return exception_handler(like_rep_logger, exc.__class__.__name__, str(exc))

    return SuccessSchema()


async def delete_like(
    username: str, tweet_id: int, session: AsyncSession
) -> Union[SuccessSchema, ErrorResponseSchema]:
    """Remove a like from a tweet."""
    user_id = await get_user_id_by(username, session)

    if not user_id:
        return exception_handler(
            like_rep_logger,
            ValueError.__class__.__name__,
            "User with this username does not exist",
        )

    if not await is_tweet_exist(tweet_id, session):
        return exception_handler(
            like_rep_logger,
            ValueError.__class__.__name__,
            "Tweet with this ID does not exist",
        )

    query = (
        delete(Like)
        .returning(Like.id)
        .where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )
    request = await session.execute(query)

    if not request.fetchone():
        return exception_handler(
            like_rep_logger,
            ValueError.__class__.__name__,
            "No like entry found for this user and tweet",
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return exception_handler(like_rep_logger, exc.__class__.__name__, str(exc))

    return SuccessSchema()
