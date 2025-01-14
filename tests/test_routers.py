import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from werkzeug.exceptions import InternalServerError

from src.main import app


@pytest.mark.usefixtures("populate_database_fixture")
class TestApi:
    @pytest.fixture(scope="class")
    async def ac(self) -> AsyncGenerator[AsyncClient, None]:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    @pytest.fixture(scope="class")
    def api_key(self):
        return {"api-key": "test"}

    @pytest.fixture(scope="function")
    async def add_tweet(self, ac, api_key):
        tweet_data = {"tweet_data": "Test tweet"}
        return await ac.post("/api/tweets", json=tweet_data, headers=api_key)

    @pytest.fixture(scope="class")
    def temp_image(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(b"fakeimagecontent")
            yield f.name
            os.remove(f.name)

    async def test_get_my_profile(self, ac, api_key):
        """Тест успешного получения профиля текущего пользователя."""
        response = await ac.get("/api/users/me", headers=api_key)

        assert response.status_code == 200

        data = response.json()
        assert data["result"] is True

        user_data = data["user"]

        assert "id" in user_data
        assert "name" in user_data
        assert user_data["name"] == "Test User"

        assert "followers" in user_data

        assert "following" in user_data

    async def test_get_user_profile(self, ac):
        """Тест для получения профиля пользователя по ID"""
        user_id = 1
        response = await ac.get(f"/api/users/{user_id}")

        assert response.status_code == 200

        json_response = response.json()
        assert "result" in json_response
        assert "user" in json_response
        assert isinstance(json_response["user"], dict)
        assert "id" in json_response["user"]
        assert "name" in json_response["user"]
        assert "followers" in json_response["user"]
        assert "following" in json_response["user"]

    async def test_get_tweets(self, ac, api_key):
        """Тест успешного получения твитов текущего пользователя."""
        response = await ac.get("/api/tweets", headers=api_key)

        assert response.status_code == 200

        data = response.json()
        assert data["result"] is True

    async def test_new_tweet(self, ac, api_key, add_tweet):
        """Тест успешного создания нового твита."""
        assert add_tweet.status_code == 201

        data = add_tweet.json()
        assert data["result"] is True
        assert "tweet_id" in data

    async def test_delete_tweet(self, ac, api_key, add_tweet):
        """Тест успешного удаления твита."""

        add_tweet_data = add_tweet.json()
        tweet_id = add_tweet_data["tweet_id"]

        delete_tweet_response = await ac.delete(
            f"/api/tweets/{tweet_id}", headers=api_key
        )

        assert delete_tweet_response.status_code == 200
        delete_tweet_data = delete_tweet_response.json()
        assert delete_tweet_data["result"] is True

    async def test_like_tweet(self, ac, api_key, add_tweet):
        """Тест успешного добавления лайка к твиту."""
        add_tweet_data = add_tweet.json()
        tweet_id = add_tweet_data["tweet_id"]

        like_response = await ac.post(f"/api/tweets/{tweet_id}/likes", headers=api_key)

        assert like_response.status_code == 201
        like_data = like_response.json()
        assert like_data["result"] is True

    async def test_unlike_tweet(self, ac, api_key, add_tweet):
        """Тест успешного удаления лайка с твита."""
        add_tweet_data = add_tweet.json()
        tweet_id = add_tweet_data["tweet_id"]

        await ac.post(f"/api/tweets/{tweet_id}/likes", headers=api_key)

        unlike_response = await ac.delete(
            f"/api/tweets/{tweet_id}/likes", headers=api_key
        )

        assert unlike_response.status_code == 200
        unlike_data = unlike_response.json()
        assert unlike_data["result"] is True

    async def test_follow_user(self, ac, api_key):
        """Тест успешного подписки на пользователя."""
        user_id = 1
        response = await ac.post(f"/api/users/{user_id}/follow", headers=api_key)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["result"] is True

    async def test_unfollow_user(self, ac, api_key):
        """Тест успешного отписки от пользователя."""
        user_id = 1
        response = await ac.delete(f"/api/users/{user_id}/follow", headers=api_key)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["result"] is True

    async def test_upload_media(self, ac, api_key, temp_image):
        """Тест успешной загрузки медиафайла."""

        file_path = Path(temp_image)
        with open(file_path, "rb") as file:
            files = {"file": (file_path.name, file, "image/jpeg")}

            # Отправка запроса
            response = await ac.post("/api/medias", files=files, headers=api_key)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["result"] is True
        assert "media_id" in response_data

    async def test_home_page(self, ac):
        """Тест для главной страницы"""
        response = await ac.get("/")

        assert response.status_code == 200

    async def test_homepage_error(self, ac, mocker):
        """Тест для обработки ошибки рендеринга"""

        mocker.patch(
            "fastapi.templating.Jinja2Templates.TemplateResponse",
            side_effect=InternalServerError("Mock exception"),
        )

        response = await ac.get("/")
        assert response.status_code == 500
        error_data = response.json()
        assert error_data["result"] is False
        assert error_data["error_type"] == "InternalServerError"
        assert (
            error_data["error_message"] == "500 Internal Server Error: Mock exception"
        )
