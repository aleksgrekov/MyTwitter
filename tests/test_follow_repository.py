import pytest

from src.database.repositories.follow_repository import (
    delete_follow,
    follow,
)
from src.schemas.base_schemas import ErrorResponseSchema, SuccessSchema


@pytest.mark.usefixtures("prepare_database")
class TestFollowModel:

    @classmethod
    def assert_error_response(cls, response, expected_message):
        assert isinstance(response, ErrorResponseSchema)
        assert response.result is False
        assert response.error_message == expected_message

    async def test_follow_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response, status_code = await follow(
                username=users_and_followers[0].username,
                following_id=users_and_followers[2].id,
                session=session,
            )
            assert isinstance(response, SuccessSchema)
            assert status_code == 201

    async def test_follow_user_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response, status_code = await follow(
                username="nonexistent_user",
                following_id=users_and_followers[1].id,
                session=session,
            )

            self.assert_error_response(
                response, "User with this username does not exist"
            )
            assert status_code == 404

    async def test_follow_following_not_found(
            self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response, status_code = await follow(
                username=users_and_followers[0].username,
                following_id=999,
                session=session,
            )

            self.assert_error_response(response, "User with this ID does not exist")
            assert status_code == 404

    async def test_remove_follow_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response, status_code = await delete_follow(
                username=users_and_followers[0].username,
                following_id=users_and_followers[1].id,
                session=session,
            )
            assert isinstance(response, SuccessSchema)
            assert status_code == 200

    async def test_remove_follow_user_not_found(
            self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response, status_code = await delete_follow(
                username="nonexistent_user",
                following_id=users_and_followers[2].id,
                session=session,
            )

            self.assert_error_response(
                response, "User with this username does not exist"
            )
            assert status_code == 404

    async def test_remove_follow_following_not_found(
            self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response, status_code = await delete_follow(
                username=users_and_followers[0].username,
                following_id=999,
                session=session,
            )

            self.assert_error_response(response, "User with this ID does not exist")
            assert status_code == 404

    async def test_remove_follow_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            response, status_code = await delete_follow(
                username=users_and_followers[0].username,
                following_id=users_and_followers[3].id,
                session=session,
            )

            self.assert_error_response(
                response,
                "No follow entry found for these follower ID and following ID",
            )
            assert status_code == 404
