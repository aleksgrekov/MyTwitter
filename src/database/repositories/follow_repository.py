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
    """Add a follow relationship."""
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
    """Remove a follow relationship."""
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
