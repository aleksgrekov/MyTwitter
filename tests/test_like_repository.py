import pytest

from src.database.models import Like, Tweet
from src.database.repositories.like_repository import (
    add_like,
    delete_like,
    is_like_exist,
)
from src.schemas.base_schemas import ErrorResponseSchema, SuccessSchema


@pytest.mark.usefixtures("prepare_database")
class TestLikeModel:

    @classmethod
    def assert_error_response(cls, response, expected_message):
        assert isinstance(response, ErrorResponseSchema)
        assert response.result is False
        assert response.error_message == expected_message

    @pytest.fixture(scope="class")
    async def test_like(self, get_session_test, users_and_followers, test_tweet):
        async with get_session_test as session:
            like = Like(user_id=users_and_followers[0].id, tweet_id=test_tweet.id)
            session.add(like)
            await session.commit()
            return like

    @pytest.mark.parametrize(
        "user_id, tweet_id, expected_result",
        [
            ("user_id", "tweet_id", True),
            (999, 999, False)
        ],
    )
    async def test_is_like_exist(
            self, get_session_test, users_and_followers, test_tweet, test_like, user_id, tweet_id, expected_result
    ):
        async with get_session_test as session:
            if user_id == "user_id":
                user_id = users_and_followers[0].id
            if tweet_id == "tweet_id":
                tweet_id = test_tweet.id

            exists = await is_like_exist(
                user_id=user_id,
                tweet_id=tweet_id,
                session=session,
            )
            assert exists is expected_result

    async def test_add_like_success(self, get_session_test, users_and_followers, test_tweet):
        async with get_session_test as session:
            response, status_code = await add_like(
                username=users_and_followers[1].username,
                tweet_id=test_tweet.id,
                session=session,
            )
            assert isinstance(response, SuccessSchema)
            assert status_code == 201

    async def test_add_like_user_not_found(self, get_session_test, test_tweet):
        async with get_session_test as session:
            response, status_code = await add_like(
                username="nonexistent_user", tweet_id=test_tweet.id, session=session
            )

            self.assert_error_response(
                response, "User with this username does not exist"
            )
            assert status_code == 404

    async def test_add_like_tweet_not_found(
            self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response, status_code = await add_like(
                username=users_and_followers[0].username, tweet_id=999, session=session
            )

            self.assert_error_response(
                response, "Tweet with this ID does not exist"
            )
            assert status_code == 404

    async def test_add_like_already_exists(
            self, get_session_test, users_and_followers, test_tweet, test_like
    ):
        async with get_session_test as session:
            response, status_code = await add_like(
                username=users_and_followers[0].username,
                tweet_id=test_tweet.id,
                session=session,
            )

            self.assert_error_response(response, "Like already exists")
            assert status_code == 409

    async def test_remove_like_success(
            self, get_session_test, users_and_followers, test_tweet, test_like
    ):
        async with get_session_test as session:
            response, status_code = await delete_like(
                username=users_and_followers[0].username,
                tweet_id=test_tweet.id,
                session=session,
            )
            assert isinstance(response, SuccessSchema)
            assert status_code == 200

    async def test_remove_like_user_not_found(self, get_session_test, test_tweet):
        async with get_session_test as session:
            response, status_code = await delete_like(
                username="nonexistent_user", tweet_id=test_tweet.id, session=session
            )

            self.assert_error_response(
                response, "User with this username does not exist"
            )
            assert status_code == 404

    async def test_remove_like_tweet_not_found(
            self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response, status_code = await delete_like(
                username=users_and_followers[0].username, tweet_id=999, session=session
            )

            self.assert_error_response(response, "Tweet with this ID does not exist")
            assert status_code == 404

    async def test_remove_like_not_found(
            self, get_session_test, users_and_followers, test_tweet
    ):
        async with get_session_test as session:
            response, status_code = await delete_like(
                username=users_and_followers[2].username,
                tweet_id=test_tweet.id,
                session=session,
            )

            self.assert_error_response(
                response, "No like entry found for this user and tweet"
            )
            assert status_code == 404
