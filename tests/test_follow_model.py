import pytest
from src.database.models import Follow
from src.database.schemas import SuccessSchema, ErrorResponseSchema


@pytest.mark.usefixtures("prepare_database")
class TestFollowModel:

    @classmethod
    def assert_error_response(cls, response, expected_message):
        assert isinstance(response, ErrorResponseSchema)
        assert response.result is False
        assert response.error_message == expected_message

    async def test_get_following_by(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            followings = await Follow.get_following_by(username=users_and_followers[0].username, session=session)
            assert users_and_followers[1].id in followings

            no_followings = await Follow.get_following_by(username="nonexistent_user", session=session)

            self.assert_error_response(no_followings, "User with this username does not exist")

    async def test_follow_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.follow(username=users_and_followers[0].username,
                                           following_id=users_and_followers[2].id, session=session)
            assert isinstance(response, SuccessSchema)

    async def test_follow_user_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.follow(username="nonexistent_user", following_id=users_and_followers[1].id,
                                           session=session)

            self.assert_error_response(response, "User with this username does not exist")

    async def test_follow_following_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.follow(username=users_and_followers[0].username, following_id=999, session=session)

            self.assert_error_response(response, "User with this ID does not exist")

    async def test_remove_follow_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.remove_follow(username=users_and_followers[0].username,
                                                  following_id=users_and_followers[2].id, session=session)
            assert isinstance(response, SuccessSchema)

    async def test_remove_follow_user_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.remove_follow(username="nonexistent_user", following_id=users_and_followers[2].id,
                                                  session=session)

            self.assert_error_response(response, "User with this username does not exist")

    async def test_remove_follow_following_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.remove_follow(username=users_and_followers[0].username, following_id=999,
                                                  session=session)

            self.assert_error_response(response, "User with this ID does not exist")

    async def test_remove_follow_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response = await Follow.remove_follow(username=users_and_followers[0].username,
                                                  following_id=users_and_followers[2].id, session=session)

            self.assert_error_response(response, "No follow entry found for this follower ID and following ID")
