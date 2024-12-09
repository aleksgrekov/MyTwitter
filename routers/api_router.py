from pathlib import Path
from typing import Annotated, Dict, Any

import aiofiles
from fastapi import (
    APIRouter, Depends, Header, status, UploadFile
)
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.utils import secure_filename

from database.models import Like, Media, Tweet, User, Follow
from database.service import create_session
from database.schemas import NewTweetDataSchema
from logger.logger_setup import get_logger
from scr.functions import allowed_file, exception_handler

routers_logger = get_logger(__name__)
api_router = APIRouter(
    prefix="/api",
    tags=["API"],
)

depends: AsyncSession = Depends(create_session)


@api_router.get("/users/me", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_my_profile(
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await User.get_user_with_followers_and_following(username=api_key, session=db)


@api_router.get("/users/{user_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_user_profile(
        user_id: int,
        db: AsyncSession = depends
):
    return await User.get_user_with_followers_and_following(user_id=user_id, session=db)


@api_router.get("/tweets", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_tweets(
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await Tweet.get_tweets_selection(username=api_key, session=db)


@api_router.post("/tweets", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def new_tweet(
        api_key: Annotated[str, Header()],
        tweet: NewTweetDataSchema,
        db: AsyncSession = depends
):
    return await Tweet.add_tweet(username=api_key, tweet=tweet, session=db)


@api_router.post("/tweets/{tweet_id}/likes", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def like(
        tweet_id: int,
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await Like.like(username=api_key, tweet_id=tweet_id, session=db)


@api_router.post("/users/{user_id}/follow", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def follow(
        user_id: int,
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await Follow.follow(username=api_key, following_id=user_id, session=db)


@api_router.post("/medias", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_media(
        api_key: Annotated[str, Header()],
        file: UploadFile,
        db: AsyncSession = depends
):
    upload_folder = Path(__file__).parent.parent / "media" / api_key
    upload_folder.mkdir(parents=True, exist_ok=True)

    if not allowed_file(file.filename):
        return exception_handler(
            routers_logger,
            "ValueError",
            "File format is not allowed. Please upload a valid file."
        )
    try:
        filename = secure_filename(file.filename)
        output_file = upload_folder / filename

        async with aiofiles.open(output_file, 'wb') as f:
            await f.write(await file.read())

        return await Media.add_media(link=str(output_file), session=db)

    except Exception as exc:
        return exception_handler(routers_logger, exc.__class__.__name__, str(exc))
    finally:
        await file.close()


@api_router.delete("/tweets/{tweet_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def delete_tweet(
        tweet_id: int,
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await Tweet.delete_tweet(username=api_key, tweet_id=tweet_id, session=db)


@api_router.delete("/tweets/{tweet_id}/likes", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def delete_like(
        tweet_id: int,
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await Like.delete_like(username=api_key, tweet_id=tweet_id, session=db)


@api_router.delete("/users/{user_id}/follow", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def delete_like(
        user_id: int,
        api_key: Annotated[str, Header()],
        db: AsyncSession = depends
):
    return await Follow.delete_follow(username=api_key, following_id=user_id, session=db)
