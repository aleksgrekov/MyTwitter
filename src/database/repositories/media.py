from typing import Union

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Media
from src.database.schemas.base import ErrorResponseSchema
from src.database.schemas.tweet import NewMediaResponseSchema
from src.functions import exception_handler
from src.logger_setup import get_logger

media_rep_logger = get_logger(__name__)


async def get_media_link_by(media_id: int, session: AsyncSession) -> str:
    """Get media link by ID"""
    query = select(Media.link).where(Media.id == media_id)
    return (await session.scalars(query)).one()


async def add_media(
    link: str, session: AsyncSession
) -> Union[NewMediaResponseSchema, ErrorResponseSchema]:
    """Add new media"""
    new_media = Media(link=link)
    session.add(new_media)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        return exception_handler(media_rep_logger, exc.__class__.__name__, str(exc))

    return NewMediaResponseSchema(media_id=new_media.id)
