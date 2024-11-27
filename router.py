from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/api",
    tags=["MyTwitter"],
)
templates = Jinja2Templates(directory="dist")


@router.get("", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def home_page(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {str(exc)}")
