import pytest

from src.database.repositories.follow_repository import delete_follow, follow
from src.handlers.exceptions import RowNotFoundException
from src.schemas.base_schemas import SuccessSchema


class TestFollowModel:
    async def test_follow_success(self, session, users_and_followers):
        """Тест успешного добавления подписки"""
        response = await follow(
            username=users_and_followers[0].username,
            following_id=users_and_followers[2].id,
            session=session,
        )
        assert isinstance(response, SuccessSchema)

    @pytest.mark.parametrize(
        "username, following_id, expected_message",
        [
            ("nonexistent", "existent", "User not found"),
            ("existent", "nonexistent", "User not found"),
        ],
    )
    async def test_follow_user_not_found(
        self, session, users_and_followers, username, following_id, expected_message
    ):
        """Тест на попытку подписаться на несуществующего пользователя"""
        if username == "existent":
            username = users_and_followers[0].username
        else:
            username = "nonexistent"

        if following_id == "existent":
            following_id = users_and_followers[1].id
        else:
            following_id = 999

        with pytest.raises(RowNotFoundException) as exc_info:
            await follow(
                username=username,
                following_id=following_id,
                session=session,
            )
        assert exc_info.value.detail == expected_message
        assert exc_info.value.status_code == 404

    async def test_remove_follow_success(self, session, users_and_followers):
        """Тест успешного удаления подписки"""
        response = await delete_follow(
            username=users_and_followers[0].username,
            following_id=users_and_followers[3].id,
            session=session,
        )
        assert isinstance(response, SuccessSchema)

    @pytest.mark.parametrize(
        "username, following_id, expected_message",
        [
            ("nonexistent", "existent", "User not found"),
            ("existent", "nonexistent", "User not found"),
            (
                "existent",
                "existent_second",
                "No follow entry found for these follower ID and following ID",
            ),
        ],
    )
    async def test_remove_follow_user_not_found(
        self,
        session,
        users_and_followers,
        username,
        following_id,
        expected_message,
    ):
        """Тест на попытку удаления подписки с несуществующим пользователем или записью"""
        if username == "existent":
            username = users_and_followers[0].username
        else:
            username = "nonexistent"

        if following_id == "existent":
            following_id = users_and_followers[2].id
        elif following_id == "existent_second":
            following_id = users_and_followers[3].id
        else:
            following_id = 999

        with pytest.raises(RowNotFoundException) as exc_info:
            await delete_follow(
                username=username,
                following_id=following_id,
                session=session,
            )
        assert exc_info.value.detail == expected_message
        assert exc_info.value.status_code == 404
