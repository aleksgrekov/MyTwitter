import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.user_repository import (
    get_user_followers,
    get_user_following,
    get_user_id_by,
    get_user_with_followers_and_following,
    is_user_exist,
)
from src.handlers.exceptions import RowNotFoundException
from src.schemas.user_schemas import UserResponseSchema


class TestUserRepository:

    async def test_check_user_exists(
        self, users_and_followers: list, session: AsyncSession
    ) -> None:
        """
        Проверяет, существует ли пользователь в базе данных по ID.
        """
        exists = await is_user_exist(user_id=users_and_followers[0].id, session=session)
        assert exists

        not_exists = await is_user_exist(100, session)
        assert not not_exists

    async def test_get_user_id_by(
        self, users_and_followers: list, session: AsyncSession
    ) -> None:
        """
        Проверяет получение ID пользователя по его имени (username).
        """
        user_id = await get_user_id_by("test_user1", session)
        assert user_id == users_and_followers[0].id

    async def test_get_user_followers(
        self, users_and_followers: list, session: AsyncSession
    ) -> None:
        """
        Проверяет получение списка подписчиков пользователя.
        """
        followers = await get_user_followers(users_and_followers[0].id, session)
        assert isinstance(followers, list)
        assert followers
        assert followers[0].id == users_and_followers[1].id

    async def test_get_user_following(
        self, users_and_followers: list, session: AsyncSession
    ) -> None:
        """
        Проверяет получение списка подписок пользователя.
        """
        following = await get_user_following(users_and_followers[0].id, session)
        assert isinstance(following, list)
        assert following
        assert following[0].id is not None

    @pytest.mark.parametrize("lookup_by", ["username", "user_id"])
    async def test_get_user_with_followers_and_following_by_username(
        self, users_and_followers: list, session: AsyncSession, lookup_by: str
    ) -> None:
        """
        Проверяет получение пользователя с его подписчиками и подписками
        по имени пользователя (username) или ID пользователя (user_id).
        """

        if lookup_by == "username":
            response = await get_user_with_followers_and_following(
                session, username=users_and_followers[0].username
            )
        elif lookup_by == "user_id":
            response = await get_user_with_followers_and_following(
                session, user_id=users_and_followers[0].id
            )
        else:
            response = None

        assert response is not None
        assert isinstance(response, UserResponseSchema)
        assert response.result is True
        assert response.user.id == users_and_followers[0].id
        assert response.user.name == users_and_followers[0].name
        assert len(response.user.followers) > 0
        assert len(response.user.following) > 0

    async def test_get_user_with_followers_and_following_missing_args(
        self, session: AsyncSession
    ) -> None:
        """
        Проверяет, что выбрасывается исключение при отсутствии необходимых параметров.
        """
        with pytest.raises(RowNotFoundException) as exc_info:
            await get_user_with_followers_and_following(session)
        assert exc_info.value.detail == "User not found"
        assert exc_info.value.status_code == 404

    async def test_get_user_with_followers_and_following_user_not_found(
        self, session: AsyncSession
    ) -> None:
        """
        Проверяет, что выбрасывается исключение при попытке получения несуществующего пользователя.
        """
        with pytest.raises(RowNotFoundException) as exc_info:
            await get_user_with_followers_and_following(
                session, username="non_existent_user"
            )
        assert exc_info.value.detail == "User not found"
        assert exc_info.value.status_code == 404
