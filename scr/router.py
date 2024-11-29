from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, Header, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database import create_session, Tweet, User

from .schemas import NewTweet

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


@router.get("/users/me")
async def get_my_profile(
        api_key: Annotated[str, Header()],
        db: AsyncSession = Depends(create_session)
):
    return await User.get_user_with_followers_and_following(username=api_key, session=db)



@router.post("/tweets", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def new_tweet(
        api_key: Annotated[str, Header()],
        tweet: NewTweet,
        db: AsyncSession = Depends(create_session)
):
    return await Tweet.add_tweet(username=api_key, tweet=tweet, session=db)


@router.post("/medias")
async def new_media(
        api_key: Annotated[str, Header()],
        db: AsyncSession = Depends(create_session)
):
    pass
