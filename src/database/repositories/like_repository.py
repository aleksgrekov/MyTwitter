from http import HTTPStatus
from typing import Tuple, Union

from sqlalchemy import delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Like
from src.database.repositories.tweet_repository import is_tweet_exist
from src.database.repositories.user_repository import get_user_id_by
from src.functions import exception_handler
from src.logger_setup import get_logger
from src.schemas.base_schemas import ErrorResponseSchema, SuccessSchema

like_rep_logger = get_logger(__name__)


async def is_like_exist(user_id: int, tweet_id: int, session: AsyncSession) -> bool:
    """Check if a like exists for a tweet by a user."""
    subquery = exists().where(Like.user_id == user_id, Like.tweet_id == tweet_id)
    query = select(subquery)
    response = await session.scalar(query)
    return response is not None and response


async def add_like(
    username: str, tweet_id: int, session: AsyncSession
) -> Tuple[Union[SuccessSchema, ErrorResponseSchema], HTTPStatus]:
    """Add a like for a tweet."""
    user_id = await get_user_id_by(username, session)

    if not user_id:
        return (
            await exception_handler(
                like_rep_logger,
                ValueError("User with this username does not exist"),
            ),
            HTTPStatus.NOT_FOUND,
        )
    elif not await is_tweet_exist(tweet_id, session):
        return (
            await exception_handler(
                like_rep_logger,
                ValueError("Tweet with this ID does not exist"),
            ),
            HTTPStatus.NOT_FOUND,
        )
    elif await is_like_exist(user_id, tweet_id, session):
        return (
            await exception_handler(like_rep_logger, ValueError("Like already exists")),
            HTTPStatus.CONFLICT,
        )

    session.add(Like(user_id=user_id, tweet_id=tweet_id))

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return await exception_handler(like_rep_logger, exc), HTTPStatus.BAD_REQUEST

    return SuccessSchema(), HTTPStatus.CREATED


async def delete_like(
    username: str, tweet_id: int, session: AsyncSession
) -> Tuple[Union[SuccessSchema, ErrorResponseSchema], HTTPStatus]:
    """Remove a like from a tweet."""
    user_id = await get_user_id_by(username, session)

    if not user_id:
        return (
            await exception_handler(
                like_rep_logger,
                ValueError("User with this username does not exist"),
            ),
            HTTPStatus.NOT_FOUND,
        )
    elif not await is_tweet_exist(tweet_id, session):
        return (
            await exception_handler(
                like_rep_logger,
                ValueError("Tweet with this ID does not exist"),
            ),
            HTTPStatus.NOT_FOUND,
        )

    query = (
        delete(Like)
        .returning(Like.id)
        .where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )
    request = await session.execute(query)

    if not request.fetchone():
        return (
            await exception_handler(
                like_rep_logger,
                ValueError("No like entry found for this user and tweet"),
            ),
            HTTPStatus.NOT_FOUND,
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return await exception_handler(like_rep_logger, exc), HTTPStatus.BAD_REQUEST

    return SuccessSchema(), HTTPStatus.OK
