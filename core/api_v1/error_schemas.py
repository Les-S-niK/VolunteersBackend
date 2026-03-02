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


class Forbidden(ErrorResponse):
    error: str = "Forbidden"
    details: str | None = "You can not access this result"


class InternalServerError(ErrorResponse):
    error: str = "Internal Server Error"


class InvalidRefreshTokenError(NotAuthorized):
    error: str = "Invalid refresh token"
