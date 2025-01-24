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
    """
    Check if a user exists by their ID.

    This function checks whether a user with the specified ID exists in the database.

    Args:
        user_id (int): The ID of the user to check.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    query = select(exists().where(User.id == user_id))
    response = await session.scalar(query)
    return response is not None and response


async def get_user_id_by(username: str, session: AsyncSession) -> Optional[int]:
    """
    Get the user ID by their username.

    This function retrieves the ID of a user given their username.

    Args:
        username (str): The username of the user.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        Optional[int]: The user ID if found, or None if the user does not exist.
    """
    query = select(User.id).where(User.username == username)
    return await session.scalar(query)


async def get_user_followers(user_id: int, session: AsyncSession) -> Sequence["User"]:
    """
    Get the followers of a user.

    This function retrieves the list of users who follow the user with the given ID.

    Args:
        user_id (int): The ID of the user whose followers are to be retrieved.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        Sequence[User]: A sequence of user objects representing the followers.
    """
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    return (await session.scalars(query)).all()


async def get_user_following(user_id: int, session: AsyncSession) -> Sequence["User"]:
    """
    Get the users a user is following.

    Retrieves the list of users that the user with the given ID is following.

    Args:
        user_id (int): The ID of the user whose following list is to be retrieved.
        session (AsyncSession): The database session used for executing queries.

    Returns:
        Sequence[User]: A sequence of user objects representing the users that the user is following.
    """
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
    """
    Get user with their followers and following list.

    This function retrieves detailed information about a user, including their followers
    and the users they are following.

    Args:
        session (AsyncSession): The database session used for executing queries.
        username (Optional[str]): The username of the user (optional, must be used
                                   if `user_id` is not provided).
        user_id (Optional[int]): The ID of the user (optional, must be used if
                                 `username` is not provided).

    Returns:
        UserResponseSchema: A schema containing the user data along with their followers
                             and following lists.

    Raises:
        RowNotFoundException: If neither `username` nor `user_id` is provided, or if
                               no user matching the criteria is found.
    """
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
