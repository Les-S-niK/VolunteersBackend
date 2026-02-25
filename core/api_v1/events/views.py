from typing import Annotated

from fastapi import APIRouter, Depends

from core.api_v1.auth import get_current_user
from core.api_v1.events.schemas import UserEvents, EventModel
from core.database.sqlalchemy.models import User, Event, UserEvent

events_router: APIRouter = APIRouter(prefix="/api/v1/events", tags=["Events"])


@events_router.get(
    path="/user_events/", description="Get all the events in which the user participated."
)
async def user_events_handler(user: Annotated[User, Depends(get_current_user)]):
    ## FIXME: Re-write this code after DATABASE update.
    user_events: list[UserEvent] | None = await UserEvent.get(user_id = user.id)
    if not user_events:
        return UserEvents(events=[])
    
    events: UserEvents = UserEvents(events=[])
    for user_event in user_events:
        event: Event | None = await Event.get_one(id=user_event.event_id)
        if not event:
            continue
        event_model: EventModel = EventModel(id=event.id, name=event.event_name, date=event.date)
        events.events.append(event_model)

    return events
