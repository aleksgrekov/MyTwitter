import pytest
from src.database.models import Like, User, Tweet
from src.database.schemas import SuccessSchema, ErrorResponseSchema


@pytest.mark.usefixtures("prepare_database")
class TestLikeModel:
    @pytest.fixture(scope="class")
    async def test_user(self, get_session_test):
        async with get_session_test as session:
            user = User(username="test_user_for_like", name="Test User for Like Model")
            session.add(user)
            await session.commit()
            return user

    @pytest.fixture(scope="class")
    async def test_tweet(self, get_session_test, test_user):
        async with get_session_test as session:
            tweet = Tweet(author_id=test_user.id, tweet_data="Test tweet", tweet_media_ids=[])
            session.add(tweet)
            await session.commit()
            return tweet

    @pytest.fixture(scope="class")
    async def test_like(self, get_session_test, test_user, test_tweet):
        async with get_session_test as session:
            like = Like(user_id=test_user.id, tweet_id=test_tweet.id)
            session.add(like)
            await session.commit()
            return like

    async def test_is_like_exist(self, get_session_test, test_user, test_tweet, test_like):
        async with get_session_test as session:
            exists = await Like.is_like_exist(user_id=test_user.id, tweet_id=test_tweet.id, session=session)
            assert exists is True

            not_exists = await Like.is_like_exist(user_id=999, tweet_id=999, session=session)
            assert not_exists is False

    async def test_add_like_success(self, get_session_test, test_user):
        async with get_session_test as session:
            tweet = Tweet(author_id=test_user.id, tweet_data="Test tweet for like", tweet_media_ids=[])
            session.add(tweet)
            await session.commit()

            response = await Like.add_like(username=test_user.username, tweet_id=tweet.id, session=session)
            assert isinstance(response, SuccessSchema)

    async def test_add_like_user_not_found(self, get_session_test, test_tweet):
        async with get_session_test as session:
            response = await Like.add_like(username="nonexistent_user", tweet_id=test_tweet.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User with this username does not exist"

    async def test_add_like_tweet_not_found(self, get_session_test, test_user):
        async with get_session_test as session:
            response = await Like.add_like(username=test_user.username, tweet_id=999, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "Tweet with this tweet_id does not exist"

    async def test_add_like_already_exists(self, get_session_test, test_user, test_tweet, test_like):
        async with get_session_test as session:
            response = await Like.add_like(username=test_user.username, tweet_id=test_tweet.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "Like already exists"

    async def test_remove_like_success(self, get_session_test, test_user, test_tweet, test_like):
        async with get_session_test as session:
            response = await Like.remove_like(username=test_user.username, tweet_id=test_tweet.id, session=session)
            assert isinstance(response, SuccessSchema)

    async def test_remove_like_user_not_found(self, get_session_test, test_tweet):
        async with get_session_test as session:
            response = await Like.remove_like(username="nonexistent_user", tweet_id=test_tweet.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User with this username does not exist"

    async def test_remove_like_tweet_not_found(self, get_session_test, test_user):
        async with get_session_test as session:
            response = await Like.remove_like(username=test_user.username, tweet_id=999, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "Tweet with this ID does not exist"

    async def test_remove_like_not_found(self, get_session_test, test_user, test_tweet):
        async with get_session_test as session:
            response = await Like.remove_like(username=test_user.username, tweet_id=test_tweet.id, session=session)
            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "No like entry found for this user and tweet"