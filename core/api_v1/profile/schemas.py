import datetime as dt
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
    city_id: Annotated[
        int,
        Field(
            default=...,
            title="City ID",
            description="City ID in the database. City where the user live.",
            examples=[123, 1234, 1],
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


class InputBodyEventModel(BaseModel):
    id: Annotated[int, Field(default=..., title="Event ID", ge=1, examples=[123, 414])]


class EventModel(InputBodyEventModel):
    name: Annotated[
        str, Field(default=..., title="Event name.", examples=["Example event."])
    ]
    datetime: Annotated[
        dt.datetime,
        Field(default=..., title="Event datetime", examples=["2026-03-05 21:15"]),
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
