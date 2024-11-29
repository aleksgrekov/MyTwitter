from typing import List

from pydantic import BaseModel, Field, ConfigDict


class NewTweet(BaseModel):
    tweet_data: str = Field(
        ...,
        max_length=280,
        title="tweet text content",
        examples=[
            "Доброе утро! Сегодня отличный день для новых идей.",
            "Проверьте нашу новую функцию! #Обновление",
        ]
    )
    tweet_media_ids: List[int] | None = Field(
        None,
        title="list of medias ids from medias table",
    )


class UserSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
