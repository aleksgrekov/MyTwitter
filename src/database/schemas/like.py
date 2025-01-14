from pydantic import BaseModel, ConfigDict, Field

from src.database.schemas.const import USERS_NAME_LENGTH


class LikeSchema(BaseModel):
    """Schema for information about a like."""

    user_id: int = Field(..., title="User ID")
    name: str = Field(
        ...,
        max_length=USERS_NAME_LENGTH,
        title="User's fullname",
        description="The name of the user who liked the tweet.",
    )

    model_config = ConfigDict(from_attributes=True)
