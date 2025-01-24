from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base_schemas import SuccessSchema
from src.schemas.const import USERS_NAME_LENGTH


class UserSchema(BaseModel):
    """Schema for user information."""

    id: int = Field(..., title="User ID")
    name: str = Field(..., max_length=USERS_NAME_LENGTH, title="User's full name")

    model_config = ConfigDict(from_attributes=True)


class UserWithFollowSchema(UserSchema):
    """Schema for user with followers and followings."""

    followers: List[UserSchema] = Field(
        default_factory=list,
        title="List of followers",
        description="Users following the current user.",
    )
    following: List[UserSchema] = Field(
        default_factory=list,
        title="List of following",
        description="Users the current user is following.",
    )


class UserResponseSchema(SuccessSchema):
    """Schema for a user data response."""

    user: UserWithFollowSchema = Field(
        ...,
        title="User data",
        description="Detailed information about the user, "
        "including their followers and following.",
    )
