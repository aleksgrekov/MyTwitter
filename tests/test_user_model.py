import pytest
from src.database.models import User, Follow
from src.database.schemas import UserResponseSchema, ErrorResponseSchema


@pytest.mark.usefixtures("prepare_database")
class TestUserModel:

    @pytest.fixture(scope='class')
    async def users(self, get_session_test):
        async with get_session_test as session:
            user1 = User(username="test_user1", name="Test User1")
            user2 = User(username="test_user2", name="Test User2")
            session.add_all([user1, user2])
            await session.flush()

            follow1 = Follow(follower_id=user1.id, following_id=user2.id)
            follow2 = Follow(follower_id=user2.id, following_id=user1.id)

            session.add_all([follow1, follow2])
            await session.commit()
            return user1, user2

    async def test_check_user_exists(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            exists = await User.is_user_exist(user_id=users_and_followers[0].id, session=session)
            assert exists is True

            not_exists = await User.is_user_exist(100, session)
            assert not_exists is False

    async def test_get_user_id_by(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            user_id = await User.get_user_id_by("test_user1", session)
            assert user_id == users_and_followers[0].id

    async def test_get_user_followers(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            followers = await User.get_user_followers(users_and_followers[0].id, session)
            assert isinstance(followers, list)
            assert len(followers) != 0
            assert followers[0].id == users_and_followers[1].id

    async def test_get_user_following(self, users_and_followers, get_session_test):
        async with get_session_test as session:
            following = await User.get_user_following(users_and_followers[0].id, session)
            assert isinstance(following, list)
            assert len(following) != 0
            assert following[0].id == users_and_followers[1].id

    @pytest.mark.parametrize("lookup_by", ["username", "user_id"])
    async def test_get_user_with_followers_and_following_by_username(self, users, get_session_test, lookup_by):
        async with get_session_test as session:
            if lookup_by == "username":
                response = await User.get_user_with_followers_and_following(session, username=users[0].username)
            elif lookup_by == "user_id":
                response = await User.get_user_with_followers_and_following(session, user_id=users[0].id)

            assert isinstance(response, UserResponseSchema)
            assert response.result is True
            assert response.user.id == users[0].id
            assert response.user.name == users[0].name
            assert len(response.user.followers) == 1
            assert len(response.user.following) == 1

    async def test_get_user_with_followers_and_following_missing_args(self, get_session_test):
        async with get_session_test as session:
            response = await User.get_user_with_followers_and_following(session)

            assert isinstance(response, ErrorResponseSchema)
            assert response.result is False
            assert response.error_message == "Missing one of argument (username or user_id)"

    async def test_get_user_with_followers_and_following_user_not_found(self, get_session_test):
        async with get_session_test as session:
            username = "non_existent_user"

            response = await User.get_user_with_followers_and_following(session, username=username)

            assert isinstance(response, ErrorResponseSchema)
            assert response.error_message == "User not found"

