from typing import Annotated, Union

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.like import add_like, delete_like
from src.database.repositories.tweet import (
    add_tweet,
    delete_tweet,
    get_tweets_selection,
)
from src.database.schemas.base import ErrorResponseSchema, SuccessSchema
from src.database.schemas.tweet import (
    NewTweetResponseSchema,
    TweetBaseSchema,
    TweetResponseSchema,
)
from src.database.service import create_session
from src.logger_setup import get_logger

tweet_router_logger = get_logger(__name__)
tweet_router = APIRouter(
    prefix="/api/tweets",
    tags=["TWEET"],
)


@tweet_router.get(
    "",
    response_model=Union[TweetResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the user's tweets",
    description="Returns a list of tweets created by the current user.",
    responses={
        200: {
            "description": "List of tweets fetched successfully",
            "model": TweetResponseSchema,
        },
        404: {"description": "Tweets not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def get_tweets(
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[TweetResponseSchema, ErrorResponseSchema]:
    return await get_tweets_selection(username=api_key, session=db)


@tweet_router.post(
    "",
    response_model=Union[NewTweetResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tweet",
    description="Creates a new tweet on behalf of the current user.",
    responses={
        201: {
            "description": "Tweet created successfully",
            "model": NewTweetResponseSchema,
        },
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def new_tweet(
    api_key: Annotated[str, Header(description="User's API key")],
    tweet: TweetBaseSchema,
    db: AsyncSession = Depends(create_session),
) -> Union[NewTweetResponseSchema, ErrorResponseSchema]:
    return await add_tweet(username=api_key, tweet=tweet, session=db)


@tweet_router.delete(
    "/{tweet_id}",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    description="Deletes a tweet by its ID if the current user is its author.",
    responses={
        200: {"description": "Tweet deleted successfully", "model": SuccessSchema},
        404: {"description": "Tweet not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def remove_tweet(
    tweet_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await delete_tweet(username=api_key, tweet_id=tweet_id, session=db)


@tweet_router.post(
    "/{tweet_id}/likes",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Like a tweet",
    description="Adds a like to the specified tweet on behalf of the current user.",
    responses={
        201: {"description": "Like added successfully", "model": SuccessSchema},
        404: {"description": "Tweet not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def like(
    tweet_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await add_like(username=api_key, tweet_id=tweet_id, session=db)


@tweet_router.delete(
    "/{tweet_id}/likes",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Remove like from a tweet",
    description="Removes a like from the specified tweet on behalf of the current user.",
    responses={
        200: {"description": "Like removed successfully", "model": SuccessSchema},
        404: {"description": "Tweet not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def remove_like(
    tweet_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await delete_like(username=api_key, tweet_id=tweet_id, session=db)
