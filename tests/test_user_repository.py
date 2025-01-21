import pytest

from src.database.repositories.user_repository import (
    get_user_followers,
    get_user_following,
    get_user_id_by,
    get_user_with_followers_and_following,
    is_user_exist,
)
from src.handlers.exceptions import RowNotFoundException
from src.schemas.user_schemas import UserResponseSchema


@pytest.mark.usefixtures("prepare_database")
class TestUserRepository:

    async def test_check_user_exists(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            exists = await is_user_exist(
                user_id=users_and_followers[0].id, session=session
            )
            assert exists

            not_exists = await is_user_exist(100, session)
            assert not not_exists

    async def test_get_user_id_by(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            user_id = await get_user_id_by("test_user1", session)
            assert user_id == users_and_followers[0].id

    async def test_get_user_followers(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            followers = await get_user_followers(users_and_followers[0].id, session)
            assert isinstance(followers, list)
            assert followers
            assert followers[0].id == users_and_followers[1].id

    async def test_get_user_following(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            following = await get_user_following(users_and_followers[0].id, session)
            assert isinstance(following, list)
            assert following
            assert following[0].id is not None

    @pytest.mark.parametrize("lookup_by", ["username", "user_id"])
    async def test_get_user_with_followers_and_following_by_username(
        self, users_and_followers, get_session_test, lookup_by
    ):
        async with get_session_test as session:
            if lookup_by == "username":
                response = await get_user_with_followers_and_following(
                    session, username=users_and_followers[0].username
                )
            elif lookup_by == "user_id":
                response = await get_user_with_followers_and_following(
                    session, user_id=users_and_followers[0].id
                )

            assert isinstance(response, UserResponseSchema)
            assert response.result is True
            assert response.user.id == users_and_followers[0].id
            assert response.user.name == users_and_followers[0].name
            assert len(response.user.followers) > 0
            assert len(response.user.following) > 0

    async def test_get_user_with_followers_and_following_missing_args(
        self, get_session_test
    ):
        async with get_session_test as session:
            with pytest.raises(RowNotFoundException) as exc_info:
                await get_user_with_followers_and_following(session)
            assert exc_info.value.detail == "User not found"
            assert exc_info.value.status_code == 404

    async def test_get_user_with_followers_and_following_user_not_found(
        self, get_session_test
    ):
        async with get_session_test as session:
            with pytest.raises(RowNotFoundException) as exc_info:
                await get_user_with_followers_and_following(
                    session, username="non_existent_user"
                )
            assert exc_info.value.detail == "User not found"
            assert exc_info.value.status_code == 404
