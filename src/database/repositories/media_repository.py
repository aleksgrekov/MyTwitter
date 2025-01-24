from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Media
from src.handlers.exceptions import IntegrityViolationException
from src.schemas.tweet_schemas import NewMediaResponseSchema


async def add_media(link: str, session: AsyncSession) -> NewMediaResponseSchema:
    """
    Add a new media entry to the database.

    This function adds a new media record with the provided `link` to the database.

    Args:
        link (str): The link of the media to be added.
        session (AsyncSession): The database session for executing queries.

    Returns:
        NewMediaResponseSchema: A schema with the ID of the newly created media entry.

    Raises:
        IntegrityViolationException: If a database integrity error occurs.
    """
    new_media = Media(link=link)
    session.add(new_media)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return NewMediaResponseSchema(media_id=new_media.id)
