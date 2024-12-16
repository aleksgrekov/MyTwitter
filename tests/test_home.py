from httpx import AsyncClient


async def test_home_page(ac: AsyncClient):
    """Тест для главной страницы"""
    response = await ac.get("/")

    assert response.status_code == 200


async def test_get_user_profile(ac: AsyncClient):
    """Тест для получения профиля пользователя по ID"""
    user_id = 1
    response = await ac.get(f"/api/users/{user_id}")

    assert response.status_code == 200

    json_response = response.json()
    assert "id" in json_response
    assert json_response["id"] == user_id
    assert "username" in json_response
    assert "name" in json_response


# @pytest.mark.asyncio
# async def test_get_user_profile_not_found(ac: AsyncClient):
#     """Тест для получения профиля пользователя с несуществующим ID"""
#     user_id = 9999
#     response = await ac.get(f"/api/users/{user_id}")
#
#     assert response.status_code == 404
#     assert response.json() == {"detail": "User not found"}
