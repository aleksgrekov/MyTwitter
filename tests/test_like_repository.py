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

    async def test_is_like_exist(
        self, get_session_test, users_and_followers, test_tweet, test_like
    ):
        async with get_session_test as session:
            exists = await is_like_exist(
                user_id=users_and_followers[0].id,
                tweet_id=test_tweet.id,
                session=session,
            )
            assert exists is True

            not_exists = await is_like_exist(user_id=999, tweet_id=999, session=session)
            assert not_exists is False

    async def test_add_like_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            tweet = Tweet(
                author_id=users_and_followers[0].id,
                tweet_data="Test tweet for like",
                tweet_media_ids=[],
            )
            session.add(tweet)
            await session.commit()

            response = await add_like(
                username=users_and_followers[0].username,
                tweet_id=tweet.id,
                session=session,
            )
            assert isinstance(response, SuccessSchema)

    async def test_add_like_user_not_found(self, get_session_test, test_tweet):
        async with get_session_test as session:
            response = await add_like(
                username="nonexistent_user", tweet_id=test_tweet.id, session=session
            )

            self.assert_error_response(
                response, "User with this username does not exist"
            )

    async def test_add_like_tweet_not_found(
        self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response = await add_like(
                username=users_and_followers[0].username, tweet_id=999, session=session
            )

            self.assert_error_response(
                response, "Tweet with this tweet_id does not exist"
            )

    async def test_add_like_already_exists(
        self, get_session_test, users_and_followers, test_tweet, test_like
    ):
        async with get_session_test as session:
            response = await add_like(
                username=users_and_followers[0].username,
                tweet_id=test_tweet.id,
                session=session,
            )

            self.assert_error_response(response, "Like already exists")

    async def test_remove_like_success(
        self, get_session_test, users_and_followers, test_tweet, test_like
    ):
        async with get_session_test as session:
            response = await delete_like(
                username=users_and_followers[0].username,
                tweet_id=test_tweet.id,
                session=session,
            )
            assert isinstance(response, SuccessSchema)

    async def test_remove_like_user_not_found(self, get_session_test, test_tweet):
        async with get_session_test as session:
            response = await delete_like(
                username="nonexistent_user", tweet_id=test_tweet.id, session=session
            )

            self.assert_error_response(
                response, "User with this username does not exist"
            )

    async def test_remove_like_tweet_not_found(
        self, get_session_test, users_and_followers
    ):
        async with get_session_test as session:
            response = await delete_like(
                username=users_and_followers[0].username, tweet_id=999, session=session
            )

            self.assert_error_response(response, "Tweet with this ID does not exist")

    async def test_remove_like_not_found(
        self, get_session_test, users_and_followers, test_tweet
    ):
        async with get_session_test as session:
            response = await delete_like(
                username=users_and_followers[0].username,
                tweet_id=test_tweet.id,
                session=session,
            )

            self.assert_error_response(
                response, "No like entry found for this user and tweet"
            )
