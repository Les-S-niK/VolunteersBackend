import datetime
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


class EventModel(BaseModel):
    id: Annotated[int, Field(default=..., title="Event ID", ge=1, examples=[123, 414])]
    name: Annotated[
        str, Field(default=..., title="Event name.", examples=["Example event."])
    ]
    date: Annotated[
        datetime.date, Field(default=..., title="Event date", examples=["2026-02-25"])
    ]


class Events(BaseModel):
    events: Annotated[
        list[EventModel],
        Field(
            default=[],
            title="Events List",
            examples=[[{"id": 123, "name": "Example event.", "date": "2026-02-25"}]],
        ),
    ]
