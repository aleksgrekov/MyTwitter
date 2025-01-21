from pathlib import Path

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from jinja2 import TemplateNotFound

from src.handlers.exceptions import RowNotFoundException
from src.handlers.handlers import exception_to_json

home_route = APIRouter(
    tags=["HomePage"],
)
path_to_template = Path(__file__).resolve().parent.parent.parent / "dist"
templates = Jinja2Templates(directory=path_to_template)


@home_route.get(
    path="/",
    response_class=HTMLResponse,
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Homepage",
    description=(
        "This endpoint renders the main homepage of the application. "
        "It returns an HTML page generated from the `index.html` template, "
        "which is the default landing page for the application."
    ),
    responses={
        200: {
            "description": "HTML page successfully rendered from the index.html template.",
            "content": {"text/html": {}},
        },
        404: {
            "description": "The `index.html` template was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "TemplateNotFound",
                        "error_message": "The requested template could not be found.",
                    }
                }
            },
        },
        422: {
            "description": "There was an error processing the template, possibly due to an invalid template file.",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "OSError",
                        "error_message": "Error occurred while rendering the homepage due to file processing issues.",
                    }
                }
            },
        },
    },
)
async def home_page(request: Request) -> HTMLResponse | JSONResponse:
    try:
        return templates.TemplateResponse(request, "index.html", {"request": request})
    except TemplateNotFound:
        return await exception_to_json(RowNotFoundException("Template not found"))
