import os
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.usefixtures("populate_database_fixture")
class TestApi:
    @pytest.fixture(scope="class")
    async def ac(self) -> AsyncGenerator[AsyncClient, None]:
        """Создание клиента для взаимодействия с API."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    @pytest.fixture(scope="class")
    def api_key(self) -> Dict[str, str]:
        """Возвращает правильный API-ключ для аутентификации."""
        return {"api-key": "test"}

    @pytest.fixture(scope="class")
    def wrong_api_key(self) -> Dict[str, str]:
        """Возвращает неправильный API-ключ для аутентификации."""
        return {"api-key": "wrong_username"}

    @pytest.fixture(scope="function")
    async def add_tweet(self, ac: AsyncClient, api_key: Dict[str, str]) -> Any:
        """Создание твита для тестов."""
        tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": []}
        return await ac.post("/api/tweets", json=tweet_data, headers=api_key)

    @pytest.fixture(scope="class")
    def temp_image(self) -> Generator[str, None, None]:
        """Создание временного изображения для тестов."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as file:
            file.write(b"fakeimagecontent")
        yield file.name
        os.remove(file.name)

    @pytest.mark.parametrize(
        "headers_value, expected_status, expected_result, expected_error",
        [
            ("api_key", 200, True, None),
            ("wrong_api_key", 404, False, "User not found"),
        ],
    )
    async def test_get_my_profile(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        headers_value: str,
        expected_status: int,
        expected_result: bool,
        expected_error: str | None,
    ) -> None:
        """Тест для получения профиля текущего пользователя, включая все возможные ответы."""
        headers = api_key if headers_value == "api_key" else wrong_api_key

        response = await ac.get("/api/users/me", headers=headers)

        assert response.status_code == expected_status

        data = response.json()
        assert data["result"] is expected_result

        if expected_result:
            user_data = data["user"]
            assert "id" in user_data
            assert "name" in user_data
            assert "followers" in user_data
            assert "following" in user_data
        else:
            assert data["error_message"] == expected_error

    @pytest.mark.parametrize(
        "user_id, expected_status, expected_result, expected_error",
        [
            (1, 200, True, None),
            (1000, 404, False, "User not found"),
        ],
    )
    async def test_get_user_profile(
        self,
        ac: AsyncClient,
        user_id: int,
        expected_status: int,
        expected_result: bool,
        expected_error: str | None,
    ) -> None:
        """Тесты для получения профиля другого пользователя."""
        response = await ac.get(f"/api/users/{user_id}")

        assert response.status_code == expected_status

        data = response.json()
        assert data["result"] is expected_result

        if expected_result:
            user_data = data["user"]
            assert "id" in user_data
            assert "name" in user_data
            assert "followers" in user_data
            assert "following" in user_data
        else:
            assert data["error_message"] == expected_error

    @pytest.mark.parametrize(
        "headers_value, expected_status, expected_result",
        [
            ("api_key", 200, True),
            ("wrong_api_key", 404, False),
        ],
    )
    async def test_get_tweets(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        headers_value: str,
        expected_status: int,
        expected_result: bool,
    ) -> None:
        """Тест получения твитов."""
        headers = api_key if headers_value == "api_key" else wrong_api_key

        response = await ac.get("/api/tweets", headers=headers)

        assert response.status_code == expected_status

        data = response.json()
        assert data["result"] is expected_result

    @pytest.mark.parametrize(
        "headers_value, tweet_data, expected_status, expected_result, expected_error_message",
        [
            (
                "api_key",
                {"tweet_data": "This is a valid tweet", "tweet_media_ids": []},
                201,
                True,
                None,
            ),
            (
                "wrong_api_key",
                {"tweet_data": "This is a valid tweet", "tweet_media_ids": []},
                404,
                False,
                "User not found",
            ),
        ],
    )
    async def test_create_tweet(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        headers_value: str,
        tweet_data: Dict[str, Any],
        expected_status: int,
        expected_result: bool,
        expected_error_message: str | None,
    ) -> None:
        """Тест для создания твита с проверкой всех возможных ответов."""
        headers = api_key if headers_value == "api_key" else wrong_api_key

        response = await ac.post("/api/tweets", json=tweet_data, headers=headers)

        assert response.status_code == expected_status
        data = response.json()

        assert data["result"] == expected_result

        if expected_result:
            assert "tweet_id" in data
        else:
            assert data["error_message"] == expected_error_message

    @pytest.mark.parametrize(
        "tweet_id, headers_value, expected_status, expected_result",
        [
            ("valid_tweet", "api_key", 200, True),
            ("valid_tweet", "wrong_api_key", 404, False),
            (999, "api_key", 403, False),
        ],
    )
    async def test_delete_tweet(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        add_tweet: Any,
        tweet_id: str,
        headers_value: str,
        expected_status: int,
        expected_result: bool,
    ) -> None:
        """Тест удаления твита."""
        if tweet_id == "valid_tweet":
            tweet_id = add_tweet.json()["tweet_id"]

        headers = api_key if headers_value == "api_key" else wrong_api_key

        response = await ac.delete(f"/api/tweets/{tweet_id}", headers=headers)

        assert response.status_code == expected_status
        response_data = response.json()
        assert response_data["result"] is expected_result

    @pytest.mark.parametrize(
        "tweet_id, headers_value, expected_status, expected_result, duplicate_like",
        [
            ("valid_tweet", "api_key", 201, True, False),
            ("valid_tweet", "api_key", 409, False, True),
            ("valid_tweet", "wrong_api_key", 404, False, False),
            (999, "api_key", 404, False, False),
        ],
    )
    async def test_like_tweet(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        add_tweet: Any,
        tweet_id: int,
        headers_value: str,
        expected_status: int,
        expected_result: bool,
        duplicate_like: bool,
    ) -> None:
        """Тест добавления лайка к твиту, включая проверку повторного лайка."""

        if tweet_id == "valid_tweet":
            tweet_id = add_tweet.json()["tweet_id"]

        headers = api_key if headers_value == "api_key" else wrong_api_key

        if duplicate_like:
            await ac.post(f"/api/tweets/{tweet_id}/likes", headers=api_key)

        like_response = await ac.post(f"/api/tweets/{tweet_id}/likes", headers=headers)

        assert like_response.status_code == expected_status
        like_data = like_response.json()
        assert like_data["result"] is expected_result

    @pytest.mark.parametrize(
        "setup_like, tweet_id, headers_value, expected_status, expected_result",
        [
            (True, "valid_tweet", "api_key", 200, True),
            (False, "valid_tweet", "api_key", 404, False),
            (True, "valid_tweet", "wrong_api_key", 404, False),
            (False, 999, "api_key", 404, False),
        ],
    )
    async def test_unlike_tweet(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        add_tweet: Any,
        setup_like: int,
        tweet_id: int,
        headers_value: str,
        expected_status: int,
        expected_result: bool,
    ) -> None:
        """Тесты для удаления лайков с твита, покрывающие все возможные сценарии."""

        if tweet_id == "valid_tweet":
            tweet_id = add_tweet.json()["tweet_id"]

        headers = api_key if headers_value == "api_key" else wrong_api_key

        if setup_like:
            await ac.post(f"/api/tweets/{tweet_id}/likes", headers=api_key)

        unlike_response = await ac.delete(
            f"/api/tweets/{tweet_id}/likes", headers=headers
        )

        assert unlike_response.status_code == expected_status
        unlike_data = unlike_response.json()
        assert unlike_data["result"] is expected_result

    @pytest.mark.parametrize(
        "headers_value, user_id, expected_status, expected_result, expected_error_message",
        [
            ("api_key", 1, 201, True, None),  # Успешное добавление подписки
            ("api_key", 9999, 404, False, "User not found"),
            ("wrong_api_key", 1, 404, False, "User not found"),
        ],
    )
    async def test_add_follow(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        headers_value: str,
        user_id: int,
        expected_status: int,
        expected_result: bool,
        expected_error_message: str,
    ) -> None:
        """Тест для добавления подписки с проверкой всех возможных ответов."""

        headers = api_key if headers_value == "api_key" else wrong_api_key

        response = await ac.post(f"/api/users/{user_id}/follow", headers=headers)

        assert response.status_code == expected_status
        data = response.json()

        assert data["result"] == expected_result

        if not expected_result:
            assert data["error_message"] == expected_error_message

    @pytest.mark.parametrize(
        "headers_value, user_id, expected_status, expected_result, expected_error_message",
        [
            ("api_key", 2, 200, True, None),
            ("api_key", 9999, 404, False, "User not found"),
            ("wrong_api_key", 1, 404, False, "User not found"),
            (
                "api_key",
                11,
                404,
                False,
                "No follow entry found for these follower ID and following ID",
            ),
        ],
    )
    async def test_unfollow_user(
        self,
        ac: AsyncClient,
        api_key: Dict[str, str],
        wrong_api_key: Dict[str, str],
        headers_value: str,
        user_id: int,
        expected_status: int,
        expected_result: bool,
        expected_error_message: str,
    ) -> None:
        """Тест отмены подписки на пользователя."""
        headers = api_key if headers_value == "api_key" else wrong_api_key

        response = await ac.delete(f"/api/users/{user_id}/follow", headers=headers)

        assert response.status_code == expected_status
        data = response.json()

        assert data["result"] == expected_result

    async def test_upload_media(
        self, ac: AsyncClient, api_key: Dict[str, str], temp_image: str
    ) -> None:
        """Тест успешной загрузки медиафайла."""

        file_path = Path(temp_image)
        with open(file_path, "rb") as file:
            files = {"file": (file_path.name, file, "image/jpeg")}

            response = await ac.post("/api/medias", files=files, headers=api_key)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["result"] is True
        assert "media_id" in response_data
