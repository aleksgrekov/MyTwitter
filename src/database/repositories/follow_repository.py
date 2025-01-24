from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow
from src.database.repositories.user_repository import get_user_id_by, is_user_exist
from src.handlers.exceptions import IntegrityViolationException, RowNotFoundException
from src.schemas.base_schemas import SuccessSchema


async def follow(
    username: str, following_id: int, session: AsyncSession
) -> SuccessSchema:
    """
    Add a follow relationship.

    This function creates a "follow" relationship where the user identified
    by `username` starts following the user identified by `following_id`.

    Args:
        username (str): The username of the follower.
        following_id (int): The ID of the user to follow.
        session (AsyncSession): The database session for executing queries.

    Returns:
        SuccessSchema: A schema indicating successful operation.

    Raises:
        RowNotFoundException: If the follower or following user does not exist.
        IntegrityViolationException: If the follow relationship already exists.
    """
    follower_id = await get_user_id_by(username, session)

    if not follower_id or not await is_user_exist(following_id, session):
        raise RowNotFoundException()

    session.add(Follow(follower_id=follower_id, following_id=following_id))

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return SuccessSchema()


async def delete_follow(
    username: str, following_id: int, session: AsyncSession
) -> SuccessSchema:
    """
    Remove a follow relationship.

    This function removes the "follow" relationship where the user identified
    by `username` unfollows the user identified by `following_id`.

    Args:
        username (str): The username of the follower.
        following_id (int): The ID of the user to unfollow.
        session (AsyncSession): The database session for executing queries.

    Returns:
        SuccessSchema: A schema indicating successful operation.

    Raises:
        RowNotFoundException: If the follower or following user does not exist,
                              or if the follow relationship is not found.
        IntegrityViolationException: If a database error occurs during the operation.
    """
    follower_id = await get_user_id_by(username, session)

    if not follower_id or not await is_user_exist(following_id, session):
        raise RowNotFoundException()

    query = (
        delete(Follow)
        .returning(Follow.following_id, Follow.follower_id)
        .where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    request = await session.execute(query)

    if not request.fetchone():
        raise RowNotFoundException(
            "No follow entry found for these follower ID and following ID"
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return SuccessSchema()
