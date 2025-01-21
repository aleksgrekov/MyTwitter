from typing import Optional, Sequence

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow, User
from src.handlers.exceptions import RowNotFoundException
from src.schemas.user_schemas import (
    UserResponseSchema,
    UserSchema,
    UserWithFollowSchema,
)


async def is_user_exist(user_id: int, session: AsyncSession) -> bool:
    """Check if a user exists by their ID."""
    query = select(exists().where(User.id == user_id))
    response = await session.scalar(query)
    return response is not None and response


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
) -> UserResponseSchema:
    """Get user with their followers and following list."""

    query = select(User)
    if username:
        query = query.where(User.username == username)
    elif user_id:
        query = query.where(User.id == user_id)
    else:
        raise RowNotFoundException()

    user = (await session.scalars(query)).one_or_none()
    if not user:
        raise RowNotFoundException()

    followers = await get_user_followers(user.id, session)
    followings = await get_user_following(user.id, session)

    return UserResponseSchema(
        user=UserWithFollowSchema(
            **UserSchema.model_validate(user).model_dump(),
            followers=[UserSchema.model_validate(follow) for follow in followers],
            following=[UserSchema.model_validate(follow) for follow in followings],
        )
    )
