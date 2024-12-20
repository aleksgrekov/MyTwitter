import pytest
from httpx import AsyncClient
from werkzeug.exceptions import InternalServerError


@pytest.mark.asyncio
async def test_home_page(ac: AsyncClient):
    """Тест для главной страницы"""
    response = await ac.get("/")

    assert response.status_code == 200


async def test_homepage_error(ac, mocker):
    """Тест для обработки ошибки рендеринга"""

    mocker.patch("fastapi.templating.Jinja2Templates.TemplateResponse", side_effect=InternalServerError("Mock exception"))

    response = await ac.get("/")
    assert response.status_code == 500
    error_data = response.json()
    assert error_data["result"] is False
    assert error_data["error_type"] == "InternalServerError"
    assert error_data["error_message"] == "500 Internal Server Error: Mock exception"
