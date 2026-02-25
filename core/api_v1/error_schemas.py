from typing import Annotated

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: Annotated[
        str,
        Field(
            default="Unspecified error",
            alias="detail",
            title="Error details.",
        ),
    ]


class NotFoundError(ErrorResponse):
    detail: str = "Not found"


class InvalidRefreshTokenError(ErrorResponse):
    detail: str = "Invalid refresh token"
