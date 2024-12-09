from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from logger.logger_setup import get_logger

from scr.functions import exception_handler

routers_logger = get_logger(__name__)
home_route = APIRouter(
    tags=["HomePage"],
)
templates = Jinja2Templates(directory="dist")


@home_route.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def home_page(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as exc:
        return exception_handler(routers_logger, exc.__class__.__name__, str(exc))
