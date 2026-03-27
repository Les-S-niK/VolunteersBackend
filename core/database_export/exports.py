from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from pandas import DataFrame
from sqlalchemy import Result

from core.database.sqlalchemy.db import CRUD, GetAction
from core.database.sqlalchemy.models import Event, Link, User, UserEvent


async def convert_table_to_dataframe(statement: GetAction) -> list[dict[str, Any]]:
    result: Result = await statement.execute()
    all_objects: list[Any] = list(result.scalars().all())

    data: list[dict[str, Any]] = [
        {
            column.name: (
                getattr(obj, column.name)
                if not isinstance(getattr(obj, column.name), datetime)
                else getattr(obj, column.name)
                .astimezone(timezone(timedelta(hours=3)))
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            for column in statement.model.__table__.columns
        }
        for obj in all_objects
    ]
    return data


async def save_all_users_to_xlsx(filename: str = "Users.xlsx") -> None:
    stmt: GetAction = CRUD.get(User).where()
    data: list[dict[str, Any]] = await convert_table_to_dataframe(stmt)

    data_frame: DataFrame = DataFrame(data)
    data_frame.to_excel(filename, sheet_name="Users")


async def save_all_links_to_xlsx(filename: str = "Links.xlsx") -> None:
    links_result: Result = (
        await CRUD.get(Link).join(User, Link.user_id == User.id).execute()
    )
    links: list[Link] = list(links_result.scalars().all())

    user_ids = {link.user_id for link in links}
    users_result: Result = await CRUD.get(User).where(User.id.in_(user_ids)).execute()
    users: list[User] = list(users_result.scalars().all())
    user_map = {user.id: user.full_name for user in users}

    data: list[dict[str, Any]] = []
    for link in links:
        row = {
            column.name: (
                getattr(link, column.name)
                if not isinstance(getattr(link, column.name), datetime)
                else getattr(link, column.name)
                .astimezone(timezone(timedelta(hours=3)))
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            for column in Link.__table__.columns
        }
        if link.user_id:
            row["full_name"] = user_map.get(link.user_id)
            data.append(row)

    data_frame: DataFrame = DataFrame(data)
    data_frame.to_excel(filename, sheet_name="Links")


async def save_all_events_to_xlsx(filename: str = "Events.xlsx") -> None:
    stmt: GetAction = CRUD.get(Event).where()
    data: list[dict[str, Any]] = await convert_table_to_dataframe(stmt)

    data_frame: DataFrame = DataFrame(data)
    data_frame.to_excel(filename, sheet_name="Events")


async def save_all_users_events_to_xlsx(filename: str = "UserEvents.xlsx") -> None:
    all_users_result = await CRUD.get(User).where().execute()
    users = list(all_users_result.scalars().all())

    user_events_result = await CRUD.get(UserEvent).where().execute()
    user_events = list(user_events_result.scalars().all())

    event_ids = {ue.event_id for ue in user_events}
    events_result = await CRUD.get(Event).where(Event.id.in_(event_ids)).execute()
    events = list(events_result.scalars().all())

    events_by_id = {event.id: event for event in events}
    user_to_event_ids = defaultdict(list)
    for ue in user_events:
        user_to_event_ids[ue.user_id].append(ue.event_id)

    def events_to_dicts(event_objects):
        return [
            {
                column.name: (
                    getattr(obj, column.name)
                    if not isinstance(getattr(obj, column.name), datetime)
                    else getattr(obj, column.name)
                    .astimezone(timezone(timedelta(hours=3)))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                for column in Event.__table__.columns
            }
            for obj in event_objects
        ]

    rows = []
    for user in users:
        event_ids_for_user = user_to_event_ids.get(user.id, [])
        event_objects = [
            events_by_id[eid] for eid in event_ids_for_user if eid in events_by_id
        ]
        convert_result = events_to_dicts(event_objects)
        rows.append({"user": f"{user.id}: {user.full_name}", "events": convert_result})

    data_frame = DataFrame(rows)
    data_frame.to_excel(filename, sheet_name="UsersEvents")
