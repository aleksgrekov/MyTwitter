from src.database.repositories.media_repository import add_media
from src.schemas.tweet_schemas import NewMediaResponseSchema


async def test_add_media_success(session):
    """Тест на успешное добавление медиа"""
    test_link = "media/test/test_media.jpg"
    response = await add_media(test_link, session)
    assert isinstance(response, NewMediaResponseSchema)
