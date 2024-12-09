from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SuccessSchema(BaseModel):
    """Base schema for success responses."""
    result: bool = Field(default=True, title="The success response field")


class NewTweetDataSchema(BaseModel):
    """Schema for creating a new tweet."""
    tweet_data: str = Field(
        ...,
        max_length=280,
        title="Tweet content",
        examples=[
            "Доброе утро! Сегодня отличный день для новых идей.",
            "Проверьте нашу новую функцию! #Обновление",
        ]
    )
    tweet_media_ids: Optional[List[int]] = Field(
        default_factory=list,
        title="List of media IDs",
        description="IDs of media associated with the tweet, from the 'medias' table."
    )


class NewTweetResponseSchema(SuccessSchema):
    """Schema of response for adding a new tweet."""
    tweet_id: int = Field(..., title="Tweet ID")


class NewMediaResponseSchema(SuccessSchema):
    """Schema of response for adding new media."""
    media_id: int = Field(..., title="Media ID")


class UserSchema(BaseModel):
    """Schema for user information."""
    id: int = Field(..., title="User ID")
    name: str = Field(..., max_length=30, title="User's full name")

    model_config = ConfigDict(from_attributes=True)


class UserWithFollowSchema(UserSchema):
    """Schema for user with followers and followings."""
    followers: List[UserSchema] = Field(
        default_factory=list,
        title="List of followers",
        description="Users following the current user."
    )
    following: List[UserSchema] = Field(
        default_factory=list,
        title="List of following",
        description="Users the current user is following."
    )


class UserResponseSchema(SuccessSchema):
    """Schema for user data response."""
    user: Optional[UserWithFollowSchema] = Field(None, title="User data")


class LikeSchema(BaseModel):
    """Schema for like information."""
    user_id: int = Field(..., title="User ID")
    name: str = Field(..., max_length=30, title="User's full name")

    model_config = ConfigDict(from_attributes=True)


class TweetSchema(BaseModel):
    """Schema for tweet information."""
    """Schema for tweet information."""
    id: int = Field(..., title="ID of the tweet")
    content: str = Field(..., max_length=280, title="Content of the tweet, max 280 characters")
    attachments: List[str] = Field(default_factory=list, title="List of associated media links")
    author: UserSchema = Field(..., title="Author of tweet data")
    likes: List[LikeSchema] = Field(default_factory=list, title="List of likes")

    model_config = ConfigDict(from_attributes=True)


class TweetResponseSchema(SuccessSchema):
    """Schema for tweets data response."""
    tweets: List[TweetSchema] = Field(default_factory=list, title="List of tweet data")
