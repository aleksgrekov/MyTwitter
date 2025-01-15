from typing import Annotated, Union

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.follow_repository import delete_follow, follow
from src.database.repositories.user_repository import (
    get_user_with_followers_and_following,
)
from src.database.service import create_session
from src.logger_setup import get_logger
from src.schemas.base_schemas import ErrorResponseSchema, SuccessSchema
from src.schemas.user_schemas import UserResponseSchema

user_router_logger = get_logger(__name__)
user_router = APIRouter(
    prefix="/api/users",
    tags=["USER"],
)


@user_router.get(
    "/me",
    response_model=Union[UserResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the current user's profile",
    description="Returns the profile data of the current user, "
    "including followers and followings.",
    responses={
        200: {
            "description": "User profile fetched successfully",
            "model": UserResponseSchema,
        },
        400: {"description": "Bad request", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def get_my_profile(
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[UserResponseSchema, ErrorResponseSchema]:
    return await get_user_with_followers_and_following(username=api_key, session=db)


@user_router.get(
    "/{user_id}",
    response_model=Union[UserResponseSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get user profile by ID",
    description="Returns the profile of a user by the specified user ID, "
    "including followers and followings.",
    responses={
        200: {
            "description": "User profile fetched successfully",
            "model": UserResponseSchema,
        },
        404: {"description": "User not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def get_user_profile(
    user_id: int, db: AsyncSession = Depends(create_session)
) -> Union[UserResponseSchema, ErrorResponseSchema]:
    return await get_user_with_followers_and_following(user_id=user_id, session=db)


@user_router.post(
    "/{user_id}/follow",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Follow a user",
    description="Creates a follow relationship "
    "between the current user and another user.",
    responses={
        201: {"description": "Successfully followed user", "model": SuccessSchema},
        404: {"description": "User not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def add_follow(
    user_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await follow(username=api_key, following_id=user_id, session=db)


@user_router.delete(
    "/{user_id}/follow",
    response_model=Union[SuccessSchema, ErrorResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Unfollow a user",
    description="Deletes a follow relationship "
    "between the current user and another user.",
    responses={
        200: {"description": "Successfully unfollowed user", "model": SuccessSchema},
        404: {"description": "User not found", "model": ErrorResponseSchema},
        500: {"description": "Internal server error", "model": ErrorResponseSchema},
    },
)
async def unfollow_user(
    user_id: int,
    api_key: Annotated[str, Header(description="User's API key")],
    db: AsyncSession = Depends(create_session),
) -> Union[SuccessSchema, ErrorResponseSchema]:
    return await delete_follow(username=api_key, following_id=user_id, session=db)
