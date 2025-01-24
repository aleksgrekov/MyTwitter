import pytest

from src.database.models import Like
from src.database.repositories.like_repository import (
    add_like,
    delete_like,
    is_like_exist,
)
from src.handlers.exceptions import RowAlreadyExists, RowNotFoundException
from src.schemas.base_schemas import SuccessSchema


class TestLikeModel:

    @pytest.fixture(scope="class")
    async def test_like(self, session, users_and_followers, test_tweet):
        """Создание начального лайка для тестов"""
        like = Like(user_id=users_and_followers[0].id, tweet_id=test_tweet.id)
        session.add(like)
        await session.commit()
        return like

    @pytest.mark.parametrize(
        "user_id, tweet_id, expected_result",
        [("user_id", "tweet_id", True), (999, 999, False)],
    )
    async def test_is_like_exist(
        self,
        session,
        users_and_followers,
        test_tweet,
        test_like,
        user_id,
        tweet_id,
        expected_result,
    ):
        """Тест на проверку существования лайка"""
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

    async def test_add_like_success(self, session, users_and_followers, test_tweet):
        """Тест на успешное добавление лайка"""
        response = await add_like(
            username=users_and_followers[1].username,
            tweet_id=test_tweet.id,
            session=session,
        )
        assert isinstance(response, SuccessSchema)

    async def test_add_like_user_not_found(self, session, test_tweet):
        """Тест на добавление лайка для несуществующего пользователя"""
        with pytest.raises(RowNotFoundException) as exc_info:
            await add_like(
                username="nonexistent_user", tweet_id=test_tweet.id, session=session
            )
        assert exc_info.value.detail == "User not found"
        assert exc_info.value.status_code == 404

    async def test_add_like_tweet_not_found(self, session, users_and_followers):
        """Тест на добавление лайка для несуществующего твита"""
        with pytest.raises(RowNotFoundException) as exc_info:
            await add_like(
                username=users_and_followers[0].username,
                tweet_id=999,
                session=session,
            )
        assert exc_info.value.detail == "Tweet with this ID does not exist"
        assert exc_info.value.status_code == 404

    async def test_add_like_already_exists(
        self, session, users_and_followers, test_tweet, test_like
    ):
        """Тест на добавление лайка, если он уже существует"""
        with pytest.raises(RowAlreadyExists) as exc_info:
            await add_like(
                username=users_and_followers[0].username,
                tweet_id=test_tweet.id,
                session=session,
            )
        assert exc_info.value.detail == "Like already exists"
        assert exc_info.value.status_code == 409

    async def test_remove_like_success(
        self, session, users_and_followers, test_tweet, test_like
    ):
        """Тест на успешное удаление лайка"""
        response = await delete_like(
            username=users_and_followers[0].username,
            tweet_id=test_tweet.id,
            session=session,
        )
        assert isinstance(response, SuccessSchema)

    async def test_remove_like_user_not_found(self, session, test_tweet):
        """Тест на удаление лайка для несуществующего пользователя"""
        with pytest.raises(RowNotFoundException) as exc_info:
            await delete_like(
                username="nonexistent_user", tweet_id=test_tweet.id, session=session
            )
        assert exc_info.value.detail == "User not found"
        assert exc_info.value.status_code == 404

    async def test_remove_like_tweet_not_found(self, session, users_and_followers):
        """Тест на удаление лайка для несуществующего твита"""
        with pytest.raises(RowNotFoundException) as exc_info:
            await delete_like(
                username=users_and_followers[0].username,
                tweet_id=999,
                session=session,
            )
        assert exc_info.value.detail == "Tweet with this ID does not exist"
        assert exc_info.value.status_code == 404

    async def test_remove_like_not_found(
        self, session, users_and_followers, test_tweet
    ):
        """Тест на удаление лайка, если запись не найдена"""
        with pytest.raises(RowNotFoundException) as exc_info:
            await delete_like(
                username=users_and_followers[2].username,
                tweet_id=test_tweet.id,
                session=session,
            )
        assert exc_info.value.detail == "No like entry found for this user and tweet"
        assert exc_info.value.status_code == 404
