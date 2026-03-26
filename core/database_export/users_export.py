from datetime import datetime, timedelta, timezone
from typing import Any

from pandas import DataFrame
from sqlalchemy import Result

from core.database.sqlalchemy.db import CRUD, GetAction
from core.database.sqlalchemy.models import Event, User, UserEvent


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


async def save_all_event_to_xlsx(filename: str = "Events.xlsx") -> None:
    stmt: GetAction = CRUD.get().where()
    data: list[dict[str, Any]] = await convert_table_to_dataframe(stmt)

    data_frame: DataFrame = DataFrame(data)
    data_frame.to_excel(filename, sheet_name="Events")


async def save_all_users_events_to_xlsx(filename: str = "UserEvents.xlsx") -> None:
    all_users_result: Result = await CRUD.get(User).where().execute()
    rows = []

    for user in all_users_result.scalars().all():
        events_statement: GetAction = (
            CRUD.get(Event)
            .join(UserEvent, UserEvent.event_id == Event.id)
            .where(UserEvent.user_id == user.id)
        )
        convert_result: list[dict[str, Any]] = await convert_table_to_dataframe(
            events_statement
        )

        rows.append({"user": f"{user.id}: {user.full_name}", "events": convert_result})

    data_frame: DataFrame = DataFrame(rows)
    data_frame.to_excel(filename, sheet_name="UsersEvents")
