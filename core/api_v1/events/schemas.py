import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class EventModel(BaseModel):
    id: Annotated[int, Field(default=..., title="Event ID", ge=1, examples=[123, 414])]
    name: Annotated[
        str, Field(default=..., title="Event name.", examples=["Example event."])
    ]
    date: Annotated[
        datetime.date, Field(default=..., title="Event date", examples=["2026-02-25"])
    ]


class UserEvents(BaseModel):
    events: Annotated[
        list[EventModel],
        Field(
            default=[],
            title="User events",
            description="Events in which the user participated.",
            examples=[[{"id": 123, "name": "Example event.", "date": "2026-02-25"}]],
        ),
    ]
