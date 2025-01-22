from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Media
from src.handlers.exceptions import IntegrityViolationException
from src.schemas.tweet_schemas import NewMediaResponseSchema


async def get_media_link_by(media_id: int, session: AsyncSession) -> str:
    """
    Get the media link by its ID.

    This function retrieves the media link associated with the given `media_id`
    from the database.

    Args:
        media_id (int): The ID of the media.
        session (AsyncSession): The database session for executing queries.

    Returns:
        str: The media link associated with the given `media_id`.

    Raises:
        RowNotFoundException: If no media is found with the given `media_id`.
    """
    query = select(Media.link).where(Media.id == media_id)
    return (await session.scalars(query)).one()


async def add_media(link: str, session: AsyncSession) -> NewMediaResponseSchema:
    """
    Add a new media entry to the database.

    This function adds a new media record with the provided `link` to the database.

    Args:
        link (str): The link of the media to be added.
        session (AsyncSession): The database session for executing queries.

    Returns:
        NewMediaResponseSchema: A schema containing the ID of the newly created media entry.

    Raises:
        IntegrityViolationException: If a database integrity error occurs (e.g., violation of unique constraints).
    """
    new_media = Media(link=link)
    session.add(new_media)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise IntegrityViolationException(str(exc))

    return NewMediaResponseSchema(media_id=new_media.id)
