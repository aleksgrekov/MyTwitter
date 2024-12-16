from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from logger.logger_setup import get_logger
from src.functions import exception_handler

routers_logger = get_logger(__name__)
home_route = APIRouter(
    tags=["HomePage"],
)
templates = Jinja2Templates(directory="dist")


@home_route.get(
    path="/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Homepage",
    description=(
            "This endpoint renders the main homepage of the application. "
            "It returns an HTML page generated from the `index.html` template."
    ),
    responses={
        200: {
            "description": "HTML page successfully rendered from the index.html template.",
            "content": {"text/html": {}}
        },
        500: {
            "description": "Internal server error occurred while rendering the homepage.",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "InternalServerError",
                        "error_message": "An unexpected error occurred while processing the request."
                    }
                }
            }
        }
    }
)
async def home_page(request: Request) -> HTMLResponse:
    """
    **Endpoint for the homepage.**

    **Purpose**:
    This endpoint renders the main homepage of the application and returns the `index.html` template.

    **Request**:
    - **request** (Request): The HTTP request object, required to render Jinja2 templates.

    **Responses**:
    - **200 OK**: Returns an HTML page rendered from the `index.html` template.
    - **500 Internal Server Error**: If an exception occurs, the error will be logged and a JSON error response will be returned.

    **Possible Errors**:
    - **500 Internal Server Error**: Could occur if there is an issue with rendering the template, like a missing file or a Jinja2 rendering error.
    """
    try:
        return templates.TemplateResponse(request, "index.html", {"request": request})
    except Exception as exc:
        return exception_handler(routers_logger, exc.__class__.__name__, str(exc))
