from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import InternalServerError, NotAuthorized
from core.api_v1.profile.schemas import EventModel, Events, UserProfile
from core.database.sqlalchemy.models import Event, User

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
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
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
    responses={
        status.HTTP_200_OK: {"model": Events},
        status.HTTP_401_UNAUTHORIZED: {
            "model": NotAuthorized,
            "description": "User not authorized.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def user_events_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> Events:
    """
    Get all the events in which the user participated.

    Returns:
        list[Event]: list of all the events where user participated.
    """
    events: list[Event] = await Event.get_events_by_user_id(user_id=user.id)
    return Events(
        events=[
            EventModel(id=event.id, datetime=event.datetime, name=event.name)
            for event in events
        ]
    )
