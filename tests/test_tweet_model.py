import pytest

from src.database.models import User, Tweet, Follow
from src.database.schemas import NewTweetDataSchema, NewTweetResponseSchema, ErrorResponseSchema, SuccessSchema, \
    TweetResponseSchema


@pytest.mark.usefixtures("prepare_database")
class TestTweetModel:

    @classmethod
    def assert_error_response(cls, response, expected_message):
        assert isinstance(response, ErrorResponseSchema)
        assert response.result is False
        assert response.error_message == expected_message

    async def test_is_tweet_exist(self, get_session_test, test_tweet):
        async with get_session_test as session:
            exists = await Tweet.is_tweet_exist(tweet_id=test_tweet.id, session=session)
            assert exists is True

            non_exists = await Tweet.is_tweet_exist(tweet_id=999, session=session)  # Non-existent tweet ID
            assert non_exists is False

    async def test_add_tweet_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            username = users_and_followers[0].username
            tweet_data = NewTweetDataSchema(tweet_data="Hello, world!", tweet_media_ids=[])

            response = await Tweet.add_tweet(username=username, tweet=tweet_data, session=session)

            assert isinstance(response, NewTweetResponseSchema)
            assert response.tweet_id is not None

    async def test_add_tweet_user_not_found(self, get_session_test):
        async with get_session_test as session:
            username = "non_existent_user"
            tweet_data = NewTweetDataSchema(tweet_data="Hello, world!", tweet_media_ids=[])

            response = await Tweet.add_tweet(username=username, tweet=tweet_data, session=session)

            self.assert_error_response(response, "User with this username does not exist")

    async def test_delete_tweet_success(self, get_session_test, users_and_followers, test_tweet):
        async with get_session_test as session:
            username = users_and_followers[0].username
            tweet_id = test_tweet.id

            response = await Tweet.delete_tweet(username=username, tweet_id=tweet_id, session=session)

            assert isinstance(response, SuccessSchema)

    async def test_delete_tweet_not_found(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            username = users_and_followers[0].username
            tweet_id = 999

            response = await Tweet.delete_tweet(username=username, tweet_id=tweet_id, session=session)

            self.assert_error_response(response, "Tweet with this ID does not exist")

    async def test_collect_tweet_data(self, get_session_test, test_tweet):
        async with get_session_test as session:
            tweet_data = await Tweet.collect_tweet_data(tweet=test_tweet, session=session)

            assert tweet_data.id == test_tweet.id
            assert tweet_data.content == test_tweet.tweet_data
            assert tweet_data.author.id == test_tweet.author.id

    async def test_get_tweets_selection_success(self, get_session_test, users_and_followers):
        async with get_session_test as session:
            session.add(
                Tweet(author_id=users_and_followers[1].id, tweet_data="Hello from second user!", tweet_media_ids=[]))
            await session.commit()

            username = users_and_followers[0].username
            response = await Tweet.get_tweets_selection(username=username, session=session)

            assert isinstance(response, TweetResponseSchema)
            assert len(response.tweets) > 0

    async def test_get_tweets_selection_user_not_found(self, get_session_test):
        async with get_session_test as session:
            username = "non_existent_user"

            response = await Tweet.get_tweets_selection(username=username, session=session)

            self.assert_error_response(response, "User with this username does not exist")
