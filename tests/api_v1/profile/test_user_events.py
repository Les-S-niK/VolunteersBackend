import datetime as dt

import pytest
from conftest import (
    api_get,
    api_post,
    assert_error_detail,
    assert_no_content,
    assert_schema,
    assert_validation_error,
)
from sqlalchemy import Result

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Event, UserEvent


USER_EVENTS_SCHEMA = {
    "events": list
}


def test_get_user_events_success(session, auth_headers):
    response = api_get(session, "/api/v1/profiles/user_events/", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert_schema(body, USER_EVENTS_SCHEMA)


def test_get_user_events_unauthorized(session):
    response = api_get(session, "/api/v1/profiles/user_events/")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_events_returns_only_current_user_events(
    session, auth_headers, current_user_id, another_user, create_event
):
    own_event_name = "pytest-user-events-own"
    foreign_event_name = "pytest-user-events-foreign"

    if another_user is None:
        pytest.skip("No second user available in database")

    own_event = await create_event(
        name=own_event_name,
        datetime=dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1),
    )
    foreign_event = await create_event(
        name=foreign_event_name,
        datetime=dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2),
    )
    await CRUD.add(UserEvent(user_id=current_user_id, event_id=own_event.id)).execute()
    await CRUD.add(UserEvent(user_id=another_user.id, event_id=foreign_event.id)).execute()

    try:
        response = api_get(session, "/api/v1/profiles/user_events/", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert_schema(body, USER_EVENTS_SCHEMA)
        assert all(isinstance(event, dict) for event in body["events"])

        own_event_payload = next(
            (event for event in body["events"] if event["id"] == own_event.id),
            None,
        )
        foreign_event_payload = next(
            (event for event in body["events"] if event["id"] == foreign_event.id),
            None,
        )

        assert own_event_payload is not None
        assert own_event_payload["name"] == own_event_name
        assert "datetime" in own_event_payload
        assert foreign_event_payload is None
    finally:
        await (
            CRUD.delete(UserEvent)
            .where(UserEvent.event_id.in_([own_event.id, foreign_event.id]))
            .execute()
        )
        await (
            CRUD.delete(Event)
            .where(Event.id.in_([own_event.id, foreign_event.id]))
            .execute()
        )


def test_post_user_event_register_unauthorized(session):
    response = api_post(session, "/api/v1/profiles/user_events/", json={"id": 1})
    assert response.status_code == 401


def test_post_user_event_register_validation_error_missing_id(session, auth_headers):
    response = api_post(session, "/api/v1/profiles/user_events/", json={}, headers=auth_headers)
    assert_validation_error(response)


def test_post_user_event_register_not_found(session, auth_headers):
    response = api_post(
        session,
        "/api/v1/profiles/user_events/",
        json={"id": 999999999},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert_error_detail(response, "Can not find event with provided ID.")


@pytest.mark.asyncio(loop_scope="session")
async def test_post_user_event_register_success_creates_user_event(
    session, auth_headers, current_user_id, create_event
):
    event = await create_event(
        name="pytest-user-events-register-success",
        datetime=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5),
    )

    try:
        response = api_post(
            session,
            "/api/v1/profiles/user_events/",
            json={"id": event.id},
            headers=auth_headers,
        )

        assert_no_content(response, 204)

        user_event_query_result: Result = (
            await CRUD.get(UserEvent)
            .where(UserEvent.user_id == current_user_id)
            .where(UserEvent.event_id == event.id)
            .execute()
        )
        user_event: UserEvent | None = user_event_query_result.scalar_one_or_none()

        assert user_event is not None
    finally:
        await (
            CRUD.delete(UserEvent)
            .where(UserEvent.user_id == current_user_id)
            .where(UserEvent.event_id == event.id)
            .execute()
        )
        await CRUD.delete(Event).where(Event.id == event.id).execute()


@pytest.mark.asyncio(loop_scope="session")
async def test_post_user_event_register_forbidden_before_start(
    session, auth_headers, create_event
):
    event = await create_event(
        name="pytest-user-events-register-future",
        datetime=dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5),
    )

    try:
        response = api_post(
            session,
            "/api/v1/profiles/user_events/",
            json={"id": event.id},
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert_error_detail(
            response,
            "User can not register for the event after 15 minutes from the moment it starts.",
        )
    finally:
        await CRUD.delete(Event).where(Event.id == event.id).execute()


@pytest.mark.asyncio(loop_scope="session")
async def test_post_user_event_register_forbidden_after_15_minutes(
    session, auth_headers, create_event
):
    event = await create_event(
        name="pytest-user-events-register-late",
        datetime=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=16),
    )

    try:
        response = api_post(
            session,
            "/api/v1/profiles/user_events/",
            json={"id": event.id},
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert_error_detail(
            response,
            "User can not register for the event after 15 minutes from the moment it starts.",
        )
    finally:
        await CRUD.delete(Event).where(Event.id == event.id).execute()
