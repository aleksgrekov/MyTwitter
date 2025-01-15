from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base_schemas import SuccessSchema
from src.schemas.const import TWEET_LENGTH
from src.schemas.like_schemas import LikeSchema
from src.schemas.user_schemas import UserSchema


class TweetBaseSchema(BaseModel):
    """Base schema for tweet data."""

    tweet_data: str = Field(
        ...,
        max_length=TWEET_LENGTH,
        title="Tweet content",
        description="The main content of the tweet, limited to 280 characters.",
        examples=[
            "Good morning! Today is a great day for new ideas.",
            "Check out our new feature! #Update",
        ],
    )
    tweet_media_ids: List[int] = Field(..., title="List of media IDs")


class NewTweetResponseSchema(SuccessSchema):
    """Schema for the response when adding a new tweet."""

    tweet_id: int = Field(..., title="Tweet ID")


class NewMediaResponseSchema(SuccessSchema):
    """Schema for the response when adding new media."""

    media_id: int = Field(
        ...,
        title="Media ID",
        description="The unique identifier of the newly uploaded media file.",
    )


class TweetSchema(BaseModel):
    """Schema for tweet information."""

    id: int = Field(..., title="Tweet ID")
    content: str = Field(
        ...,
        max_length=TWEET_LENGTH,
        title="Tweet content",
        description="The main text of the tweet, limited to 280 characters.",
    )
    attachments: List[str] = Field(
        default_factory=list,
        title="Media attachments",
        description="A list of URLs of media files associated with the tweet.",
    )
    author: UserSchema = Field(
        ...,
        title="Tweet author",
        description="Information about the author of the tweet.",
    )
    likes: List[LikeSchema] = Field(
        default_factory=list,
        title="Likes",
        description="A list of users who liked the tweet.",
    )

    model_config = ConfigDict(from_attributes=True)


class TweetResponseSchema(SuccessSchema):
    """Schema for the response containing tweet data."""

    tweets: List[TweetSchema] = Field(
        default_factory=list,
        title="Tweets",
        description="A list of tweets with detailed information.",
    )
