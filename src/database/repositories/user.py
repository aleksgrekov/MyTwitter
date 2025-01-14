from typing import Optional, Sequence, Union

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow, User
from src.database.schemas.base import ErrorResponseSchema
from src.database.schemas.user import (
    UserResponseSchema,
    UserSchema,
    UserWithFollowSchema,
)
from src.functions import exception_handler
from src.logger_setup import get_logger

user_rep_logger = get_logger(__name__)


async def is_user_exist(user_id: int, session: AsyncSession) -> bool:
    """Check if a user exists by their ID."""
    query = select(exists().where(User.id == user_id))
    return await session.scalar(query)


async def get_user_id_by(username: str, session: AsyncSession) -> Optional[int]:
    """Get the user ID by their username."""
    query = select(User.id).where(User.username == username)
    return await session.scalar(query)


async def get_user_followers(user_id: int, session: AsyncSession) -> Sequence["User"]:
    """Get the followers of a user."""
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    return (await session.scalars(query)).all()


async def get_user_following(user_id: int, session: AsyncSession) -> Sequence["User"]:
    """Get the users a user is following."""
    query = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    return (await session.scalars(query)).all()


async def get_user_with_followers_and_following(
    session: AsyncSession,
    username: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Union[UserResponseSchema, ErrorResponseSchema]:
    """Get user with their followers and following list."""
    if not username and not user_id:
        return exception_handler(
            user_rep_logger,
            ValueError.__class__.__name__,
            "Missing one of argument (username or user_id)",
        )

    query = select(User)
    if username:
        query = query.where(User.username == username)
    elif user_id:
        query = query.where(User.id == user_id)

    user = (await session.scalars(query)).one_or_none()
    if not user:
        return exception_handler(
            user_rep_logger, ValueError.__class__.__name__, "User not found"
        )

    followers = await get_user_followers(user.id, session)
    followings = await get_user_following(user.id, session)

    return UserResponseSchema(
        user=UserWithFollowSchema(
            **UserSchema.model_validate(user).model_dump(),
            followers=[UserSchema.model_validate(follow) for follow in followers],
            following=[UserSchema.model_validate(follow) for follow in followings],
        )
    )
