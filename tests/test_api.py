from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_get_my_profile(ac, api_key):
    """Тест успешного получения профиля текущего пользователя."""
    response = await ac.get(
        "/api/users/me",
        headers=api_key
    )

    assert response.status_code == 200

    data = response.json()
    assert data['result'] is True

    user_data = data['user']

    assert 'id' in user_data
    assert user_data['id'] == 11
    assert 'name' in user_data
    assert user_data['name'] == 'Test Name'

    assert 'followers' in user_data

    assert 'following' in user_data


@pytest.mark.asyncio
async def test_get_user_profile(ac):
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


@pytest.mark.asyncio
async def test_get_tweets(ac, api_key):
    """Тест успешного получения твитов текущего пользователя."""
    response = await ac.get(
        "/api/tweets",
        headers=api_key
    )

    assert response.status_code == 200

    data = response.json()
    assert data['result'] is True


@pytest.mark.asyncio
async def test_new_tweet(ac, api_key, add_tweet):
    """Тест успешного создания нового твита."""
    assert add_tweet.status_code == 201

    data = add_tweet.json()
    assert data['result'] is True
    assert 'tweet_id' in data


@pytest.mark.asyncio
async def test_delete_tweet(ac, api_key, add_tweet):
    """Тест успешного удаления твита."""

    add_tweet_data = add_tweet.json()
    tweet_id = add_tweet_data["tweet_id"]

    delete_tweet_response = await ac.delete(
        f"/api/tweets/{tweet_id}",
        headers=api_key
    )

    assert delete_tweet_response.status_code == 200
    delete_tweet_data = delete_tweet_response.json()
    assert delete_tweet_data["result"] is True


@pytest.mark.asyncio
async def test_like_tweet(ac, api_key, add_tweet):
    """Тест успешного добавления лайка к твиту."""
    add_tweet_data = add_tweet.json()
    tweet_id = add_tweet_data["tweet_id"]

    like_response = await ac.post(
        f"/api/tweets/{tweet_id}/likes",
        headers=api_key
    )

    assert like_response.status_code == 201
    like_data = like_response.json()
    assert like_data["result"] is True


@pytest.mark.asyncio
async def test_unlike_tweet(ac, api_key, add_tweet):
    """Тест успешного удаления лайка с твита."""
    add_tweet_data = add_tweet.json()
    tweet_id = add_tweet_data["tweet_id"]

    await ac.post(
        f"/api/tweets/{tweet_id}/likes",
        headers=api_key
    )

    unlike_response = await ac.delete(
        f"/api/tweets/{tweet_id}/likes",
        headers=api_key
    )

    assert unlike_response.status_code == 200
    unlike_data = unlike_response.json()
    assert unlike_data["result"] is True


@pytest.mark.asyncio
async def test_follow_user(ac, api_key):
    """Тест успешного подписки на пользователя."""
    user_id = 1
    response = await ac.post(
        f"/api/users/{user_id}/follow",
        headers=api_key
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["result"] is True


@pytest.mark.asyncio
async def test_unfollow_user(ac, api_key):
    """Тест успешного отписки от пользователя."""
    user_id = 1
    response = await ac.delete(
        f"/api/users/{user_id}/follow",
        headers=api_key
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["result"] is True


@pytest.mark.asyncio
async def test_upload_media(ac, api_key, temp_image):
    """Тест успешной загрузки медиафайла."""

    file_path = Path(temp_image)
    with open(file_path, "rb") as file:
        files = {
            "file": (file_path.name, file, "image/jpeg")
        }

        # Отправка запроса
        response = await ac.post(
            "/api/medias",
            files=files,
            headers=api_key
        )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["result"] is True
    assert "media_id" in response_data
