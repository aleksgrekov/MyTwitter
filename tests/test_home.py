import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_home_page(ac: AsyncClient):
    """Тест для главной страницы"""
    response = await ac.get("/")

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_user_profile(ac: AsyncClient):
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

# @pytest.mark.asyncio
# async def test_get_all_tweets(ac):
#     """Тест получения списка всех твитов"""
#     response = await ac.get("/api/tweets", headers={"api-key": "test"})
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) > 0

# @pytest.mark.asyncio
# async def test_get_user_profile_not_found(ac: AsyncClient):
#     """Тест для получения профиля пользователя с несуществующим ID"""
#     user_id = 9999
#     response = await ac.get(f"/api/users/{user_id}")
#
#     assert response.status_code == 404
#     assert response.json() == {"detail": "User not found"}
