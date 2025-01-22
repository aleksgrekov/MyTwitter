import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tweet
from src.database.repositories.tweet_repository import (
    add_tweet,
    collect_tweet_data,
    delete_tweet,
    get_tweets_selection,
    is_tweet_exist,
)
from src.handlers.exceptions import PermissionException, RowNotFoundException
from src.schemas.base_schemas import SuccessSchema
from src.schemas.tweet_schemas import (
    NewTweetResponseSchema,
    TweetBaseSchema,
    TweetResponseSchema,
)


@pytest.mark.usefixtures("prepare_database")
class TestTweetModel:

    @pytest.mark.parametrize(
        "tweet_id, expected_result", [("exist", True), (999, False)]
    )
    async def test_is_tweet_exist(
        self,
        get_session_test: AsyncSession,
        test_tweet: Tweet,
        tweet_id: str | int,
        expected_result: bool,
    ) -> None:
        """Тестирует наличие твита в базе данных по идентификатору."""
        tweet_id = test_tweet.id if tweet_id == "exist" else tweet_id

        async with get_session_test as session:
            exists = await is_tweet_exist(tweet_id=tweet_id, session=session)
            assert exists is expected_result

    async def test_add_tweet_success(
        self, get_session_test: AsyncSession, users_and_followers: list
    ) -> None:
        """Тестирует успешное добавление твита."""
        async with get_session_test as session:
            username = users_and_followers[0].username
            tweet_data = TweetBaseSchema(tweet_data="Hello, world!", tweet_media_ids=[])

            response = await add_tweet(
                username=username, tweet=tweet_data, session=session
            )

            assert isinstance(response, NewTweetResponseSchema)
            assert response.tweet_id is not None

    async def test_add_tweet_user_not_found(
        self, get_session_test: AsyncSession
    ) -> None:
        """Тестирует добавление твита для несуществующего пользователя."""
        tweet_data = TweetBaseSchema(tweet_data="Hello, world!", tweet_media_ids=[])

        async with get_session_test as session:
            with pytest.raises(RowNotFoundException) as exc_info:
                await add_tweet(
                    username="non_existent_user", tweet=tweet_data, session=session
                )
            assert exc_info.value.detail == "User not found"
            assert exc_info.value.status_code == 404

    async def test_delete_tweet_success(
        self,
        get_session_test: AsyncSession,
        users_and_followers: list,
        test_tweet: Tweet,
    ) -> None:
        """Тестирует успешное удаление твита."""
        async with get_session_test as session:
            username = users_and_followers[0].username
            tweet_id = test_tweet.id

            response = await delete_tweet(
                username=username, tweet_id=tweet_id, session=session
            )

            assert isinstance(response, SuccessSchema)

    async def test_delete_tweet_not_found(
        self, get_session_test: AsyncSession, users_and_followers: list
    ) -> None:
        """Тестирует удаление твита, который не существует."""
        async with get_session_test as session:
            with pytest.raises(PermissionException) as exc_info:
                await delete_tweet(
                    username=users_and_followers[0].username,
                    tweet_id=999,
                    session=session,
                )
            assert (
                exc_info.value.detail
                == "User with username='test_user1' can't delete tweet with tweet_id=999"
            )
            assert exc_info.value.status_code == 403

    async def test_collect_tweet_data(
        self, get_session_test: AsyncSession, test_tweet: Tweet
    ) -> None:
        """Тестирует сбор данных о твите для дальнейшего использования."""
        async with get_session_test as session:
            tweet_data = await collect_tweet_data(tweet=test_tweet, session=session)

            assert tweet_data.id == test_tweet.id
            assert tweet_data.content == test_tweet.tweet_data
            assert tweet_data.author.id == test_tweet.author.id

    async def test_get_tweets_selection_success(
        self, get_session_test: AsyncSession, users_and_followers: list
    ) -> None:
        """Тестирует успешное получение списка твитов пользователя."""
        async with get_session_test as session:
            session.add(
                Tweet(
                    author_id=users_and_followers[1].id,
                    tweet_data="Hello from second user!",
                    tweet_media_ids=[],
                )
            )
            await session.commit()

            username = users_and_followers[0].username
            response = await get_tweets_selection(username=username, session=session)

            assert isinstance(response, TweetResponseSchema)
            assert len(response.tweets) > 0

    async def test_get_tweets_selection_user_not_found(
        self, get_session_test: AsyncSession
    ) -> None:
        """Тестирует попытку получения твитов для несуществующего пользователя."""
        async with get_session_test as session:
            with pytest.raises(RowNotFoundException) as exc_info:
                await get_tweets_selection(
                    username="non_existent_user", session=session
                )
            assert exc_info.value.detail == "User not found"
            assert exc_info.value.status_code == 404
