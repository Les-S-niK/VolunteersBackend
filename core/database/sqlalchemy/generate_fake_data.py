from random import choice, randint

from faker import Faker
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.auth import hash_password
from core.database.sqlalchemy.db import CRUD, drop_db, init_db
from core.database.sqlalchemy.models import (
    Event,
    Good,
    Link,
    PurchaseStatuses,
    Report,
    User,
    UserEvent,
    UserGood,
)

fake = Faker()


async def fill_fake_users():
    async with CRUD() as session:
        for i in range(100):
            user: User = User(
                full_name=fake.name(),
                birth=fake.date_of_birth(),
                city_id=randint(100, 1000),
                passport=f"{randint(1_000, 10_000)} {randint(100_000, 1_000_000)}",
                phone_number=f"+7{randint(1_000_000_000, 10_000_000_000)}",
                points=randint(0, 100),
                telegram_id=randint(100_000_000, 1_000_000_000)
                if randint(0, 4)
                else None,
                password=hash_password(str(i + 1)),
            )
            print(user)
            await CRUD.add(user, session=session).execute()


async def fill_fake_events():
    async with CRUD() as session:
        for _ in range(100):
            event: Event = Event(
                name=hex(randint(1024, 65536))[2:],
                datetime=fake.date_time(),
            )
            await CRUD.add(event, session=session).execute()


async def fill_fake_links():
    async with CRUD() as session:
        for i in range(100):
            is_url_none: bool = bool(not randint(0, 4))
            is_url_proh: bool = bool(randint(0, 1))

            link: Link = Link(
                link=fake.url(),
                is_prohibited=None if is_url_none else is_url_proh,
                priority=randint(0, 10),
                user_id=i + 1,
            )
            try:
                await CRUD.add(link, session=session).execute()
            except SQLAlchemyError as e:
                print(e)


async def fill_fake_users_events():
    users_result: Result = await CRUD.get(User).where().execute()
    users: list[User] = list(users_result.scalars().all())
    events_result: Result = await CRUD.get(Event).where().execute()
    events: list[Event] = list(events_result.scalars().all())

    if not users or not events:
        return
    async with CRUD() as session:
        if randint(0, 2):
            for user in users:
                for event in events:
                    if not randint(0, 3):
                        user_event: UserEvent = UserEvent(
                            user_id=user.id, event_id=event.id
                        )
                        await CRUD.add(user_event, session=session).execute()


async def fill_fake_reports():
    users_result: Result = await CRUD.get(User).where().execute()
    users: list[User] = list(users_result.scalars().all())

    async with CRUD() as session:
        for user in users:
            if not randint(0, 1):
                continue
            report: Report = Report(
                title=fake.user_name(),
                description=fake.color_name(),
                user_id=user.id,
            )
            CRUD.add(report, session=session)


async def fill_fake_goods():
    async with CRUD() as session:
        for _ in range(100):
            good: Good = Good(
                image_url=fake.url(),
                price=randint(0, 1000),
                amount=randint(0, 20),
                name=fake.name_male(),
            )
            try:
                await CRUD.add(good, session=session).execute()
            except SQLAlchemyError as e:
                print(e)


async def fill_fake_user_good():
    users_result: Result = await CRUD.get(User).where().execute()
    users: list[User] = list(users_result.scalars().all())
    goods_result: Result = await CRUD.get(Good).where().execute()
    goods: list[Good] = list(goods_result.scalars().all())

    if not users or not goods:
        return
    async with CRUD() as session:
        if not randint(0, 5):
            for user in users:
                for good in goods:
                    if not randint(0, 3):
                        status: PurchaseStatuses = choice(
                            [
                                PurchaseStatuses.frozen,
                                PurchaseStatuses.denied,
                                PurchaseStatuses.purchased,
                            ]
                        )
                        user_good: UserGood = UserGood(
                            user_id=user.id, good_id=good.id, status=status
                        )
                        await CRUD.add(user_good, session=session).execute()


async def recreate_db() -> None:
    await drop_db()
    await init_db()

    await fill_fake_users()
    await fill_fake_links()
    await fill_fake_events()
    await fill_fake_users_events()
    await fill_fake_reports()
    await fill_fake_goods()
    await fill_fake_user_good()
    print("End")
