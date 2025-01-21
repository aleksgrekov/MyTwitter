from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Media
from src.handlers.exceptions import IntegrityViolationException
from src.schemas.tweet_schemas import NewMediaResponseSchema


async def get_media_link_by(media_id: int, session: AsyncSession) -> str:
    """Get media link by ID"""
    query = select(Media.link).where(Media.id == media_id)
    return (await session.scalars(query)).one()


async def add_media(link: str, session: AsyncSession) -> NewMediaResponseSchema:
    """Add new media"""
    new_media = Media(link=link)
    session.add(new_media)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return NewMediaResponseSchema(media_id=new_media.id)
