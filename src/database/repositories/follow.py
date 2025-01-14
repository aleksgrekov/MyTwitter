from typing import Sequence, Union

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow
from src.database.repositories.user import get_user_id_by, is_user_exist
from src.database.schemas.base import ErrorResponseSchema, SuccessSchema
from src.functions import exception_handler
from src.logger_setup import get_logger

follow_rep_logger = get_logger(__name__)


async def get_following_by(
    username: str, session: AsyncSession
) -> Union[Sequence[int], ErrorResponseSchema]:
    """Get following by username"""
    user_id = await get_user_id_by(username, session)

    if not user_id:
        return exception_handler(
            follow_rep_logger,
            ValueError.__class__.__name__,
            "User with this username does not exist",
        )

    query = select(Follow.following_id).where(Follow.follower_id == user_id)
    return (await session.scalars(query)).all()


async def follow(
    username: str, following_id: int, session: AsyncSession
) -> Union[SuccessSchema, ErrorResponseSchema]:
    """Add a follow relationship."""
    follower_id = await get_user_id_by(username, session)

    if not follower_id:
        return exception_handler(
            follow_rep_logger,
            ValueError.__class__.__name__,
            "User with this username does not exist",
        )
    elif not await is_user_exist(following_id, session):
        return exception_handler(
            follow_rep_logger,
            ValueError.__class__.__name__,
            "User with this ID does not exist",
        )

    session.add(Follow(follower_id=follower_id, following_id=following_id))

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return exception_handler(follow_rep_logger, exc.__class__.__name__, str(exc))

    return SuccessSchema()


async def delete_follow(
    username: str, following_id: int, session: AsyncSession
) -> Union[SuccessSchema, ErrorResponseSchema]:
    """Remove a follow relationship."""
    follower_id = await get_user_id_by(username, session)

    if not follower_id:
        return exception_handler(
            follow_rep_logger,
            ValueError.__class__.__name__,
            "User with this username does not exist",
        )

    if not await is_user_exist(following_id, session):
        return exception_handler(
            follow_rep_logger,
            ValueError.__class__.__name__,
            "User with this ID does not exist",
        )

    query = (
        delete(Follow)
        .returning(Follow.following_id, Follow.follower_id)
        .where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    request = await session.execute(query)

    if not request.fetchone():
        return exception_handler(
            follow_rep_logger,
            ValueError.__class__.__name__,
            "No follow entry found for this follower ID and following ID",
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return exception_handler(follow_rep_logger, exc.__class__.__name__, str(exc))

    return SuccessSchema()
