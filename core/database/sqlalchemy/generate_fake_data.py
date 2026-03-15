from random import choice, randint

from faker import Faker
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.auth import hash_password
from core.database.sqlalchemy.db import CRUD, drop_db, init_db
from core.database.sqlalchemy.models import (
    Event,
    Item,
    Link,
    PurchaseStatuses,
    Report,
    ReportStatuses,
    User,
    UserEvent,
    UserItem,
)

fake = Faker()


async def fill_fake_users():
    async with CRUD() as session:
        for i in range(100):
            user: User = User(
                full_name=fake.name(),
                birth=fake.date_of_birth(),
                city_id=1,
                passport=f"{randint(1_000, 10_000)} {randint(100_000, 1_000_000)}",
                phone_number=f"+7{randint(1_000_000_000, 10_000_000_000)}",
                points=randint(0, 100),
                telegram_id=randint(100_000_000, 1_000_000_000)
                if randint(0, 4)
                else None,
                password=hash_password(str(i + 1)),
            )
            await CRUD.add(user, session=session).execute()
            await session.commit()


async def fill_fake_events():
    async with CRUD() as session:
        for _ in range(100):
            event: Event = Event(
                name=hex(randint(1024, 65536))[2:],
                datetime=fake.date_time(),
            )
            await CRUD.add(event, session=session).execute()
            await session.commit()


async def fill_fake_links():
    async with CRUD() as session:
        for i in range(200):
            is_url_none: bool = bool(not randint(0, 4))
            is_url_proh: bool = bool(randint(0, 1))

            link: Link = Link(
                link=fake.url(),
                is_prohibited=None if is_url_none else is_url_proh,
                priority=randint(0, 10),
                user_id=randint(0, 100),
            )
            try:
                await CRUD.add(link, session=session).execute()
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
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
                if not randint(0, 3):
                    event: Event = choice(events)
                    events.remove(event)
                    user_event: UserEvent = UserEvent(
                        user_id=user.id, event_id=event.id
                    )
                    await CRUD.add(user_event, session=session).execute()
                    await session.commit()


async def fill_fake_reports():
    users_result: Result = await CRUD.get(User).where().execute()
    users: list[User] = list(users_result.scalars().all())

    async with CRUD() as session:
        for user in users:
            if not randint(0, 1):
                continue

            status: ReportStatuses = choice(
                [
                    ReportStatuses.answered,
                    ReportStatuses.unanswered,
                ]
            )
            report: Report = Report(
                title=fake.user_name(),
                description=fake.color_name(),
                status=status,
                user_id=user.id,
            )
            CRUD.add(report, session=session)
            await session.commit()


async def fill_fake_items():
    async with CRUD() as session:
        for _ in range(100):
            item: Item = Item(
                image_url=fake.url(),
                price=randint(0, 1000),
                amount=randint(0, 20),
                name=fake.name_male(),
            )
            try:
                await CRUD.add(item, session=session).execute()
            except SQLAlchemyError as e:
                print(e)
            await session.commit()


async def fill_fake_user_item():
    users_result: Result = await CRUD.get(User).where().execute()
    users: list[User] = list(users_result.scalars().all())
    items_result: Result = await CRUD.get(Item).where().execute()
    items: list[Item] = list(items_result.scalars().all())

    if not users or not items:
        return
    async with CRUD() as session:
        for user in users:
            item: Item = choice(items)
            items.remove(item)
            if not randint(0, 3):
                status: PurchaseStatuses = choice(
                    [
                        PurchaseStatuses.frozen,
                        PurchaseStatuses.denied,
                        PurchaseStatuses.purchased,
                    ]
                )
                user_item: UserItem = UserItem(
                    user_id=user.id, item_id=item.id, status=status
                )
                await CRUD.add(user_item, session=session).execute()
                await session.commit()


async def recreate_db() -> None:
    await drop_db()
    await init_db()

    await fill_fake_users()
    await fill_fake_links()
    await fill_fake_events()
    await fill_fake_users_events()
    await fill_fake_reports()
    await fill_fake_items()
    await fill_fake_user_item()
    print("End")
