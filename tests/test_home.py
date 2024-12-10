import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_home_page(ac: AsyncClient):
    """Тест для главной страницы"""
    response = await ac.get("/")
    assert response.status_code == 200
    assert "<title>" in response.text
    assert "Home Page" in response.text