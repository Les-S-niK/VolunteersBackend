import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import (
    Forbidden,
    InternalServerError,
    NotAuthorized,
    NotFoundError,
)
from core.api_v1.http_exceptions import internal_server_error
from core.api_v1.profile.schemas import (
    EventModel,
    Events,
    InputBodyEventModel,
    UserProfile,
)
from core.database.sqlalchemy.db import CRUD
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
async def user_events_get_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> Events:
    """
    Get all the events in which the user participated.

    Returns:
        list[Event]: list of all the events where user participated.
    """
    try:
        events_query_result: Result = (
            await CRUD.get(Event)
            .join(UserEvent, UserEvent.event_id == Event.id)
            .where(UserEvent.user_id == user.id)
            .execute()
        )
    except SQLAlchemyError:
        raise internal_server_error
    events: list[Event] = list(events_query_result.scalars().all())

    return Events(
        events=[
            EventModel(id=event.id, datetime=event.datetime, name=event.name)
            for event in events
        ]
    )


@profile_router.post(
    path="/user_events/",
    description="Register the user for the event. ( The user can do that within 15 minutes from the moment event starts. )",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "No content."},
        status.HTTP_401_UNAUTHORIZED: {
            "model": NotAuthorized,
            "description": "User not authorized.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": Forbidden,
            "description": "User can not register for the event after 15 minutes from the moment it starts.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundError,
            "description": "Can not find event with the provided ID.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_events_register_handler(
    user: Annotated[User, Depends(get_current_user)],
    event: Annotated[InputBodyEventModel, Body()],
) -> Response:
    """
    Register the user for the event.
    The user can do that within 15 minutes after it starts.

    Returns:
        Response: status 204 NoContent when the user successfully registered for the event.
    """
    async with CRUD() as session:
        try:
            event_query_result: Result = (
                await CRUD.get(Event, session=session)
                .where(Event.id == event.id)
                .execute()
            )
        except SQLAlchemyError:
            raise internal_server_error
        event_model: Event | None = event_query_result.scalar_one_or_none()

        if not event_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Can not find event with provided ID.",
            )

        now_time: dt.datetime = dt.datetime.now(dt.timezone.utc)
        max_register_time: dt.timedelta = dt.timedelta(minutes=15)
        event_start: dt.datetime = event_model.datetime
        timediff: dt.timedelta = now_time - event_start

        if timediff.total_seconds() < 0 or timediff > max_register_time:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can not register for the event after 15 minutes from the moment it starts.",
            )

        try:
            new_user_event: UserEvent = UserEvent(
                event_id=event_model.id, user_id=user.id
            )
            await CRUD.add(new_user_event, session=session).execute()
        except SQLAlchemyError:
            raise internal_server_error

    return Response(status_code=status.HTTP_204_NO_CONTENT)
