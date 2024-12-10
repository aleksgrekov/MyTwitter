from typing import Annotated, Union
from fastapi import APIRouter, Header, status, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Like, Media, Tweet, User, Follow
from database.schemas import NewTweetDataSchema, UserResponseSchema, TweetResponseSchema, NewMediaResponseSchema, \
    SuccessSchema, ErrorResponseSchema, NewTweetResponseSchema
from database.service import create_session
from logger.logger_setup import get_logger
from scr.functions import exception_handler, save_uploaded_file

routers_logger = get_logger(__name__)
api_router = APIRouter(
    prefix="/api",
    tags=["API"],
)


@api_router.get(
    "/users/me",
    response_model=Union[UserResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the current user's profile",
    description="Returns the profile data of the current user, including followers and followings.",
    responses={
        200: {"description": "User profile fetched successfully", "model": UserResponseSchema},
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def get_my_profile(
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[UserResponseSchema, ErrorResponseSchema]:
    return await User.get_user_with_followers_and_following(username=api_key, session=db)


@api_router.get(
    "/users/{user_id}",
    response_model=Union[UserResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get user profile by ID",
    description="Returns the profile of a user by the specified user ID, including followers and followings.",
    responses={
        200: {"description": "User profile fetched successfully", "model": UserResponseSchema},
        404: {"description": "User not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def get_user_profile(
        user_id: int,
        db: AsyncSession = Depends(create_session)
) -> Union[UserResponseSchema, ErrorResponseSchema]:
    return await User.get_user_with_followers_and_following(user_id=user_id, session=db)


@api_router.get(
    "/tweets",
    response_model=Union[TweetResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the user's tweets",
    description="Returns a list of tweets created by the current user.",
    responses={
        200: {"description": "List of tweets fetched successfully", "model": TweetResponseSchema},
        404: {"description": "Tweets not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def get_tweets(
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[TweetResponseSchema, ErrorResponseSchema]:
    return await Tweet.get_tweets_selection(username=api_key, session=db)


@api_router.post(
    "/tweets",
    response_model=Union[NewTweetResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tweet",
    description="Creates a new tweet on behalf of the current user.",
    responses={
        201: {"description": "Tweet created successfully", "model": NewTweetResponseSchema},
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def new_tweet(
        api_key: Annotated[str, Header(description="User's API key")],
        tweet: NewTweetDataSchema,
        db: AsyncSession = Depends(create_session)
) -> Union[NewTweetResponseSchema, ErrorResponseSchema]:
    return await Tweet.add_tweet(username=api_key, tweet=tweet, session=db)


@api_router.delete(
    "/tweets/{tweet_id}",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    description="Deletes a tweet by its ID if the current user is its author.",
    responses={
        200: {"description": "Tweet deleted successfully", "model": SuccessSchema},
        404: {"description": "Tweet not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def delete_tweet(
        tweet_id: int,
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await Tweet.delete_tweet(username=api_key, tweet_id=tweet_id, session=db)


@api_router.post(
    "/tweets/{tweet_id}/likes",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Like a tweet",
    description="Adds a like to the specified tweet on behalf of the current user.",
    responses={
        201: {"description": "Like added successfully", "model": SuccessSchema},
        404: {"description": "Tweet not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def like(
        tweet_id: int,
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await Like.like(username=api_key, tweet_id=tweet_id, session=db)


@api_router.delete(
    "/tweets/{tweet_id}/likes",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Remove like from a tweet",
    description="Removes a like from the specified tweet on behalf of the current user.",
    responses={
        200: {"description": "Like removed successfully", "model": SuccessSchema},
        404: {"description": "Tweet not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def delete_like(
        tweet_id: int,
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await Like.delete_like(username=api_key, tweet_id=tweet_id, session=db)


@api_router.post(
    "/users/{user_id}/follow",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Follow a user",
    description="Creates a follow relationship between the current user and another user.",
    responses={
        201: {"description": "Successfully followed user", "model": SuccessSchema},
        404: {"description": "User not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def follow(
        user_id: int,
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await Follow.follow(username=api_key, following_id=user_id, session=db)


@api_router.delete(
    "/users/{user_id}/follow",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Unfollow a user",
    description="Deletes a follow relationship between the current user and another user.",
    responses={
        200: {"description": "Successfully unfollowed user", "model": SuccessSchema},
        404: {"description": "User not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def unfollow_user(
        user_id: int,
        api_key: Annotated[str, Header(description="User's API key")],
        db: AsyncSession = Depends(create_session)
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await Follow.delete_follow(username=api_key, following_id=user_id, session=db)


@api_router.post(
    "/medias",
    response_model=Union[NewMediaResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a media file",
    description="Uploads a media file to the server and returns a link to the file.",
    responses={
        201: {"description": "Media file uploaded successfully", "model": NewMediaResponseSchema},
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    }
)
async def upload_media(
        api_key: Annotated[str, Header(description="User's API key")],
        file: UploadFile,
        db: AsyncSession = Depends(create_session)
) -> Union[NewMediaResponseSchema, ErrorResponseSchema]:
    try:
        link = await save_uploaded_file(api_key, file)
        return await Media.add_media(link, session=db)
    except Exception as exc:
        return exception_handler(routers_logger, exc.__class__.__name__, str(exc))
    finally:
        await file.close()
