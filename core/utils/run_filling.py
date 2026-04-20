import asyncio
import re
from datetime import datetime
from os import path

import pandas as pd
from sqlalchemy import select

from core.api_v1.auth.hashing import hash_password
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import User, Event, UserEvent

DEFAULT_CITY_ID = 826
DEFAULT_EVENT_DT = datetime(2024, 1, 1)
EMPTY_PASSWORD_HASH = hash_password("default")


def extract_city_id(full_id: int) -> int:
    s = str(full_id)
    match = re.search(r"0+[1-9]", s)
    if match:
        city_part = s[: match.start()]
        return int(city_part) if city_part else DEFAULT_CITY_ID
    return DEFAULT_CITY_ID


async def transfer_excel_to_db(filename: str = "db.xlsx") -> None:
    filepath = path.join(path.dirname(__file__), filename)
    if not path.exists(filepath):
        print(f"Файл {filename} не найден.")
        return

    df = pd.read_excel(filepath)
    df.columns = [col.replace(" ", "_") for col in df.columns]
    # Замена NaN на None
    df = df.where(pd.notnull(df), None)

    async with CRUD() as session:
        for row in df.itertuples(index=False):
            full_user_id = getattr(row, "ID")
            if full_user_id is None:
                continue

            try:
                full_user_id = int(full_user_id)
            except ValueError, TypeError:
                continue

            full_name_raw = getattr(row, "ФИО")
            if full_name_raw is None:
                continue
            full_name_raw = str(full_name_raw)
            parts = full_name_raw.split()
            birth = None
            if parts and re.match(r"\d{2}\.\d{2}\.\d{4}", parts[-1]):
                try:
                    birth = datetime.strptime(parts.pop(), "%d.%m.%Y").date()
                except ValueError:
                    pass
            full_name = " ".join(parts)

            passport_val = getattr(row, "Паспорт")
            if pd.isna(passport_val) or passport_val in (None, "none", "0"):
                passport = None
            else:
                passport = str(passport_val)

            phone_val = getattr(row, "Телефон")
            if (
                pd.isna(phone_val)
                or phone_val is None
                or str(phone_val).lower() == "none"
            ):
                phone = None
            else:
                phone = str(phone_val)

            points_val = getattr(row, "Баллы")
            points = int(points_val) if points_val is not None else 0

            password_val = getattr(row, "Пароль")
            # Хэшируем пароль, если он есть, иначе используем хэш "default"
            if password_val is not None and not pd.isna(password_val):
                password = hash_password(str(password_val))
            else:
                password = EMPTY_PASSWORD_HASH

            telegram_val = getattr(row, "Telegram_ID")
            if telegram_val is not None and not pd.isna(telegram_val):
                try:
                    telegram_id = int(float(telegram_val))
                except ValueError, TypeError:
                    telegram_id = None
            else:
                telegram_id = None

            city_id = extract_city_id(full_user_id)

            user = User(
                full_name=full_name,
                birth=birth,
                passport=passport,
                phone_number=phone,
                points=points,
                password=password,
                telegram_id=telegram_id,
                city_id=city_id,
            )

            existing = await session.execute(
                select(User).where(User.id == full_user_id)
            )
            if existing.scalar_one_or_none():
                await session.merge(user)
            else:
                await CRUD.add(user, session=session).execute()

            attendance_val = getattr(row, "Посещаемость")
            if attendance_val and isinstance(attendance_val, str):
                for event_name in [
                    e.strip() for e in attendance_val.split(";") if e.strip()
                ]:
                    ev = await session.execute(
                        select(Event).where(Event.name == event_name)
                    )
                    event = ev.scalar_one_or_none()
                    if not event:
                        event = Event(
                            name=event_name,
                            description="Нет",
                            points=0,
                            datetime=DEFAULT_EVENT_DT,
                        )
                        await CRUD.add(event, session=session).execute()
                    ue = await session.execute(
                        select(UserEvent).where(
                            UserEvent.user_id == user.id, UserEvent.event_id == event.id
                        )
                    )
                    if not ue.scalar_one_or_none():
                        await CRUD.add(
                            UserEvent(user_id=user.id, event_id=event.id),
                            session=session,
                        ).execute()

        await session.commit()
        print("Перенос завершён.")


async def main():
    await transfer_excel_to_db()


if __name__ == "__main__":
    asyncio.run(main())
