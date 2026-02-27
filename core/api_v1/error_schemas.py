from typing import Annotated

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: Annotated[
        str,
        Field(
            default="Unspecified error",
            alias="error",
            title="Error information.",
        ),
    ]
    details: str | None


class NotFoundError(ErrorResponse):
    error: str = "Not found"


class NotAuthorized(ErrorResponse):
    error: str = "Not authorized"
    details: str | None = "You are not authorized to access this resource."


class InvalidRefreshTokenError(NotAuthorized):
    error: str = "Invalid refresh token"
