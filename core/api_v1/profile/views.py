import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_409_CONFLICT

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import (
    ConflictError,
    Forbidden,
    InternalServerError,
    NotAuthorized,
    NotFoundError,
    TooManyRequestsError,
)
from core.api_v1.http_exceptions import internal_server_error, not_authorized
from core.api_v1.profile.schemas import (
    EventModel,
    Events,
    InputBodyEventModel,
    UserProfile,
)
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Event, User, UserEvent

EVENT_AVAILABLE_TIME: dt.timedelta = dt.timedelta(minutes=15)

profile_router: APIRouter = APIRouter(
    prefix="/api/v1/profiles",
    tags=["Profile"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": NotAuthorized},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": TooManyRequestsError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)


@profile_router.get(
    path="/user_profile/",
    description="Get user's profile.",
    responses={
        status.HTTP_200_OK: {"model": UserProfile},
    },
)
async def profiles_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    """
    Get user's id, city id and points from the profile.
    """
    return UserProfile(id=user.id, city_id=user.city_id, points=user.points)


@profile_router.get(
    path="/user_events/",
    description="Get all the events in which the user participated.",
    responses={
        status.HTTP_200_OK: {"model": Events},
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
            EventModel(
                id=event.id,
                name=event.name,
                description=event.description,
                points=event.points,
                datetime=event.datetime,
            )
            for event in events
        ]
    )


@profile_router.post(
    path="/user_events/",
    description="Register the user for the event. ( The user can do that within 15 minutes from the moment event starts. )",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "No content."},
        status.HTTP_403_FORBIDDEN: {
            "model": Forbidden,
            "description": "User can not register for the event after 15 minutes from the moment it starts.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundError,
            "description": "Can not find event with the provided ID.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictError,
            "description": "User already registered for this event.",
        },
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
    now_time: dt.datetime = dt.datetime.now(dt.timezone.utc)
    async with CRUD() as session:
        async with session.begin():
            try:
                event_query_result: Result = (
                    await CRUD.get(Event, session=session)
                    .where(Event.id == event.id)
                    .with_for_update()
                    .execute()
                )
                event_model: Event | None = event_query_result.scalar_one_or_none()
                if not event_model:
                    await session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Can not find event with provided ID.",
                    )

                event_start: dt.datetime = event_model.datetime
                timediff: dt.timedelta = now_time - event_start

                if timediff.total_seconds() < 0 or timediff > EVENT_AVAILABLE_TIME:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"User can not register for the event after {EVENT_AVAILABLE_TIME} minutes from the moment it starts.",
                    )

                user_result: Result = (
                    await CRUD.get(User, session=session)
                    .where(User.id == user.id)
                    .with_for_update()
                    .execute()
                )
                user_from_db: User | None = user_result.scalar_one_or_none()
                if not user_from_db:
                    raise not_authorized

                existing_registration: Result = await (
                    CRUD.get(UserEvent, session=session)
                    .where(
                        UserEvent.event_id == event_model.id,
                        UserEvent.user_id == user.id,
                    )
                    .with_for_update()
                    .execute()
                )
                if existing_registration.scalar_one_or_none():
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT, detail="Already registered."
                    )

                await (
                    CRUD.update(User, session=session)
                    .where(User.id == user_from_db.id)
                    .values(points=user_from_db.points + event_model.points)
                    .execute()
                )
                new_user_event: UserEvent = UserEvent(
                    event_id=event_model.id, user_id=user_from_db.id
                )
                await CRUD.add(new_user_event, session=session).execute()
            except SQLAlchemyError:
                await session.rollback()
                raise internal_server_error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@profile_router.get(
    path="/available_events/",
    description="Get all the events in which the user can participate right now.",
    responses={
        status.HTTP_200_OK: {"model": Events},
    },
)
async def available_events_handler(
    _: Annotated[User, Depends(get_current_user)],
) -> Events:
    now_time: dt.datetime = dt.datetime.now(dt.timezone.utc)
    try:
        events_query_result: Result = (
            await CRUD.get(Event)
            .where(Event.datetime.between(now_time - EVENT_AVAILABLE_TIME, now_time))
            .execute()
        )
    except SQLAlchemyError:
        raise internal_server_error
    events: list[Event] = list(events_query_result.scalars().all())

    return Events(
        events=[
            EventModel(
                id=event.id,
                name=event.name,
                description=event.description,
                points=event.points,
                datetime=event.datetime,
            )
            for event in events
        ]
    )
