from pydantic import BaseModel, Field


class SuccessSchema(BaseModel):
    """Base schema for success responses."""

    result: bool = Field(
        default=True,
        title="The success response field",
        description="Indicates if the operation was successful.",
    )


class ErrorResponseSchema(BaseModel):
    """Schema for an error response."""

    result: bool = Field(
        False,
        title="Operation result",
        description="Indicates that the operation was unsuccessful.",
    )
    error_type: str = Field(
        ..., title="Error type", description="The type or class of the error."
    )
    error_message: str = Field(
        ..., title="Error message", description="A descriptive message about the error."
    )
