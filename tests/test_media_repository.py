import pytest
from sqlalchemy.exc import NoResultFound

from src.database.models import Media
from src.database.repositories.media import MediaRepository


@pytest.mark.usefixtures("prepare_database")
class TestMediaModel:
    @pytest.fixture(scope="class")
    async def test_media(self, get_session_test):
        async with get_session_test as session:
            media = Media(link="media/test/test_media.jpg")
            session.add(media)
            await session.commit()
            return media

    async def test_get_media_link_by_valid_id(self, get_session_test, test_media):
        async with get_session_test as session:
            link = await MediaRepository.get_media_link_by(
                media_id=test_media.id, session=session
            )
            assert link == test_media.link

    async def test_get_media_link_by_invalid_id(self, get_session_test):
        async with get_session_test as session:
            with pytest.raises(NoResultFound):
                await MediaRepository.get_media_link_by(media_id=999, session=session)
