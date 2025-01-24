from typing import Annotated, Union

from fastapi import APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.like_repository import add_like, delete_like
from src.database.repositories.tweet_repository import (
    add_tweet,
    delete_tweet,
    get_tweets_selection,
)
from src.database.service import create_session
from src.handlers.handlers import secure_request
from src.schemas.base_schemas import ErrorResponseSchema, SuccessSchema
from src.schemas.tweet_schemas import (
    NewTweetResponseSchema,
    TweetBaseSchema,
    TweetResponseSchema,
)

tweet_router = APIRouter(
    prefix="/api",
    tags=["TWEET"],
)


@tweet_router.get(
    "/tweets",
    response_model=Union[TweetResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get tweets from followed users",
    description="Returns a list of tweets created by users the current user is following.",
    responses={
        200: {
            "description": "List of tweets fetched successfully",
            "model": TweetResponseSchema,
        },
        404: {"description": "User not found", "model": ErrorResponseSchema},
    },
)
async def get_tweets(
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> JSONResponse:
    coroutine = get_tweets_selection(username=api_key, session=db)
    return await secure_request(coroutine)


@tweet_router.post(
    "/tweets",
    response_model=Union[NewTweetResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tweet",
    description="Creates a new tweet for the current user.",
    responses={
        201: {
            "description": "Tweet created successfully",
            "model": NewTweetResponseSchema,
        },
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        404: {"description": "User not found", "model": ErrorResponseSchema},
    },
)
async def new_tweet(
    api_key: Annotated[str, Header(description="User's API key")],
    tweet: TweetBaseSchema,
    db: AsyncSession = Depends(create_session),
) -> JSONResponse:
    coroutine = add_tweet(username=api_key, tweet=tweet, session=db)
    return await secure_request(coroutine)


@tweet_router.delete(
    "/tweets/{tweet_id}",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    description="Deletes a tweet by its ID if the current user is its author.",
    responses={
        200: {"description": "Tweet deleted successfully", "model": SuccessSchema},
        400: {
            "description": "User can't delete this tweet",
            "model": ErrorResponseSchema,
        },
        404: {"description": "User not found", "model": ErrorResponseSchema},
    },
)
async def remove_tweet(
    tweet_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> JSONResponse:
    coroutine = delete_tweet(username=api_key, tweet_id=tweet_id, session=db)
    return await secure_request(coroutine)


@tweet_router.post(
    "/tweets/{tweet_id}/likes",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Like a tweet",
    description="Adds a like to the specified tweet.",
    responses={
        201: {"description": "Like added successfully", "model": SuccessSchema},
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        404: {"description": "Tweet or User not found ", "model": ErrorResponseSchema},
        409: {"description": "Like already exists", "model": ErrorResponseSchema},
    },
)
async def like(
    tweet_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> JSONResponse:
    coroutine = add_like(username=api_key, tweet_id=tweet_id, session=db)
    return await secure_request(coroutine)


@tweet_router.delete(
    "/tweets/{tweet_id}/likes",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Remove a like from a tweet",
    description="Removes a like from the specified tweet.",
    responses={
        200: {"description": "Like removed successfully", "model": SuccessSchema},
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        404: {
            "description": "Tweet, Like or User not found",
            "model": ErrorResponseSchema,
        },
    },
)
async def remove_like(
    tweet_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> JSONResponse:
    coroutine = delete_like(username=api_key, tweet_id=tweet_id, session=db)
    return await secure_request(coroutine)
