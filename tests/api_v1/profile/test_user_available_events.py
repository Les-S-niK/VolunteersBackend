"""AI-generated tests for /available_events/ endpoint."""

import datetime as dt

import pytest
from conftest import (
    api_get,
    assert_schema,
)
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Event

EVENT_AVAILABLE_TIME: dt.timedelta = dt.timedelta(minutes=15)


AVAILABLE_EVENTS_SCHEMA = {"events": list}


def test_available_events_unauthorized(session):
    """Доступ без токена должен быть запрещён."""
    response = api_get(session, "/api/v1/profiles/available_events/")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_available_events_empty(session, auth_headers):
    """Когда нет доступных событий, возвращается пустой список."""
    response = api_get(
        session, "/api/v1/profiles/available_events/", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert_schema(body, AVAILABLE_EVENTS_SCHEMA)
    assert body["events"] == []


@pytest.mark.asyncio(loop_scope="session")
async def test_available_events_returns_only_relevant_events(
    session, auth_headers, create_event
):
    """Возвращаются только события, попадающие в интервал [now - AVAILABLE_TIME, now]."""
    now = dt.datetime.now(dt.timezone.utc)
    available_start = now - EVENT_AVAILABLE_TIME

    # Создаём события в разных временных диапазонах
    event_inside = await create_event(
        name="inside_window",
        description="sus",
        points=10.0,
        datetime=now - dt.timedelta(minutes=5),  # внутри окна
    )
    event_boundary_start = await create_event(
        name="boundary_start",
        description="sus",
        points=5.0,
        datetime=available_start + dt.timedelta(seconds=1),  # граница начала с запасом
    )
    event_boundary_end = await create_event(
        name="boundary_end",
        description="sus",
        points=7.0,
        datetime=now - dt.timedelta(milliseconds=1),  # граница конца с запасом
    )
    event_too_early = await create_event(
        name="too_early",
        description="sus",
        points=3.0,
        datetime=available_start - dt.timedelta(seconds=1),  # чуть раньше
    )
    event_future = await create_event(
        name="future",
        points=8.0,
        description="sus",
        datetime=now + dt.timedelta(minutes=1),  # в будущем
    )

    try:
        response = api_get(
            session, "/api/v1/profiles/available_events/", headers=auth_headers
        )
        assert response.status_code == 200
        body = response.json()
        assert_schema(body, AVAILABLE_EVENTS_SCHEMA)

        event_ids = [e["id"] for e in body["events"]]
        assert event_inside.id in event_ids
        assert event_boundary_start.id in event_ids
        assert event_boundary_end.id in event_ids
        assert event_too_early.id not in event_ids
        assert event_future.id not in event_ids

        # Проверяем, что каждое событие содержит ожидаемые поля
        for event_data in body["events"]:
            assert "id" in event_data
            assert "name" in event_data
            assert "description" in event_data
            assert "points" in event_data
            assert "datetime" in event_data
    finally:
        # Чистим созданные события
        all_events = [
            event_inside,
            event_boundary_start,
            event_boundary_end,
            event_too_early,
            event_future,
        ]
        for ev in all_events:
            await CRUD.delete(Event).where(Event.id == ev.id).execute()
