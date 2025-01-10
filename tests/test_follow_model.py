import pytest
from src.database.models import Follow, User
from src.database.schemas import SuccessSchema, ErrorResponseSchema


@pytest.mark.usefixtures("prepare_database")
class TestFollowModel:
    @pytest.fixture(scope="class")
    async def test_user(self, get_session_test):
        async with get_session_test as session:
            user = User(username="test_user_for_follow", name="Test User for Follow Model")
            session.add(user)
            await session.commit()
            return user

    @pytest.fixture(scope="class")
    async def another_user(self, get_session_test):
        async with get_session_test as session:
            user = User(username="another_user_for_follow", name="Another User for Follow Model")
            session.add(user)
            await session.commit()
            return user

    @pytest.fixture(scope="class")
    async def test_follow(self, get_session_test, test_user, another_user):
        async with get_session_test as session:
            follow = Follow(follower_id=test_user.id, following_id=another_user.id)
            session.add(follow)
            await session.commit()
            return follow

    async def test_get_following_by(self, get_session_test, test_user, another_user, test_follow):
        async with get_session_test as session:
            followings = await Follow.get_following_by(username=test_user.username, session=session)
            assert another_user.id in followings

            no_followings = await Follow.get_following_by(username="nonexistent_user", session=session)
            assert isinstance(no_followings, ErrorResponseSchema)
            assert no_followings.error_message == "User with this username does not exist"

    async def test_follow_success(self, get_session_test, test_user):
        async with get_session_test as session:
            another_user = User(username="second_another_user_for_follow", name="Another User for Follow Model")
            session.add(another_user)
            await session.commit()

            response = await Follow.follow(username=test_user.username, following_id=another_user.id, session=session)
            assert isinstance(response, SuccessSchema)

    async def test_follow_user_not_found(self, get_session_test, another_user):
        async with get_session_test as session:
            response = await Follow.follow(username="nonexistent_user", following_id=another_user.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User with this username does not exist"

    async def test_follow_following_not_found(self, get_session_test, test_user):
        async with get_session_test as session:
            response = await Follow.follow(username=test_user.username, following_id=999, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User with this ID does not exist"

    async def test_remove_follow_success(self, get_session_test, test_user, another_user):
        async with get_session_test as session:
            response = await Follow.remove_follow(username=test_user.username, following_id=another_user.id, session=session)
            assert isinstance(response, SuccessSchema)

    async def test_remove_follow_user_not_found(self, get_session_test, another_user):
        async with get_session_test as session:
            response = await Follow.remove_follow(username="nonexistent_user", following_id=another_user.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User with this username does not exist"

    async def test_remove_follow_following_not_found(self, get_session_test, test_user):
        async with get_session_test as session:
            response = await Follow.remove_follow(username=test_user.username, following_id=999, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User with this ID does not exist"

    async def test_remove_follow_not_found(self, get_session_test, test_user, another_user):
        async with get_session_test as session:
            response = await Follow.remove_follow(username=test_user.username, following_id=another_user.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "No follow entry found for this follower ID and following ID"