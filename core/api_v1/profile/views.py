from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import NotAuthorized
from core.api_v1.profile.schemas import EventModel, UserEvents, UserProfile
from core.database.sqlalchemy.models import Event, User, UserEvent

profile_router: APIRouter = APIRouter(prefix="/api/v1/profiles", tags=["Profile"])


@profile_router.get(
    path="/user_profile/",
    description="Get user's profile.",
    responses={
        status.HTTP_200_OK: {"model": UserProfile},
        status.HTTP_401_UNAUTHORIZED: {
            "model": NotAuthorized,
            "description": "User not authorized.",
        },
    },
)
async def profiles_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    """
    Get user's id, full name and points from the profile.
    """
    return UserProfile(id=user.id, full_name=user.full_name, points=user.points)


@profile_router.get(
    path="/user_events/",
    description="Get all the events in which the user participated.",
    # responses={401: {"model": NotAuthorized, "description": "User not authorized."}},
)
async def user_events_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> UserEvents:
    ## FIXME:
    ## Iplement database query to get all the events in which user participated.
    ## Re-write handler logic after query is ready.
    ## Test endpoint.
    user_events: list[UserEvent] | None = await UserEvent.get(user_id=user.id)
    if not user_events:
        return UserEvents(events=[])

    events: UserEvents = UserEvents(events=[])
    for user_event in user_events:
        event: Event | None = await Event.get_one(id=user_event.event_id)
        if not event:
            continue
        event_model: EventModel = EventModel(
            id=event.id, name=event.name, date=event.date
        )
        events.events.append(event_model)

    return events
