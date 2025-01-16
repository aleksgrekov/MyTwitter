from http import HTTPStatus
from typing import Tuple, Union

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Follow
from src.database.repositories.user_repository import get_user_id_by, is_user_exist
from src.functions import exception_handler
from src.logger_setup import get_logger
from src.schemas.base_schemas import ErrorResponseSchema, SuccessSchema

follow_rep_logger = get_logger(__name__)


async def follow(
    username: str, following_id: int, session: AsyncSession
) -> Tuple[Union[SuccessSchema, ErrorResponseSchema], HTTPStatus]:
    """Add a follow relationship."""
    follower_id = await get_user_id_by(username, session)

    if not follower_id or not await is_user_exist(following_id, session):
        return (
            await exception_handler(
                follow_rep_logger,
                ValueError("User does not exist"),
            ),
            HTTPStatus.NOT_FOUND,
        )

    session.add(Follow(follower_id=follower_id, following_id=following_id))

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return await exception_handler(follow_rep_logger, exc), HTTPStatus.BAD_REQUEST

    return SuccessSchema(), HTTPStatus.CREATED


async def delete_follow(
    username: str, following_id: int, session: AsyncSession
) -> Tuple[Union[SuccessSchema, ErrorResponseSchema], HTTPStatus]:
    """Remove a follow relationship."""
    follower_id = await get_user_id_by(username, session)

    if not follower_id or not await is_user_exist(following_id, session):
        return (
            await exception_handler(
                follow_rep_logger,
                ValueError("User does not exist"),
            ),
            HTTPStatus.NOT_FOUND,
        )

    query = (
        delete(Follow)
        .returning(Follow.following_id, Follow.follower_id)
        .where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    request = await session.execute(query)

    if not request.fetchone():
        return (
            await exception_handler(
                follow_rep_logger,
                ValueError(
                    "No follow entry found for these follower ID and following ID"
                ),
            ),
            HTTPStatus.NOT_FOUND,
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return await exception_handler(follow_rep_logger, exc), HTTPStatus.BAD_REQUEST

    return SuccessSchema(), HTTPStatus.OK
