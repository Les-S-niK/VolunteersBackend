from typing import Annotated

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: Annotated[
        int,
        Field(
            default=...,
            title="User's ID",
            description="User's ID in the database.",
            examples=[123, 1234, 1],
        ),
    ]
    full_name: Annotated[
        str,
        Field(
            default=...,
            title="User's full name.",
            examples=["Elena Olegovna Lebedeva"],
        ),
    ]
    points: Annotated[
        int,
        Field(
            default=...,
            title="User's points.",
            description="User's activity points.",
            examples=[1000, 6452],
        ),
    ]
