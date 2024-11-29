import os
from pathlib import Path
from typing import Annotated, Dict, Any

import aiofiles
from fastapi import APIRouter, Depends, Header, Request, status, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.utils import secure_filename

from database.models import Media, Tweet, User
from database.service import create_session
from database.schemas import NewTweet

from functions import allowed_file, exception_handler

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
        return exception_handler(exc.__class__.__name__, str(exc))


@router.get("/users/me", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
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


@router.post("/medias", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_media(
        api_key: Annotated[str, Header()],
        file: UploadFile,
        db: AsyncSession = Depends(create_session)
):
    upload_folder = Path(__file__).parent.parent / "media" / api_key
    os.makedirs(upload_folder, exist_ok=True)

    try:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            contents = await file.read()
            output_file = upload_folder / filename
            async with aiofiles.open(output_file, 'wb') as f:
                await f.write(contents)
        else:
            return exception_handler(
                "ValueError",
                "File format is not allowed. Please upload a valid file."
            )
        return await Media.add_media(link=str(output_file), session=db)
    except Exception as exc:
        return exception_handler(exc.__class__.__name__, str(exc))
    finally:
        await file.close()
