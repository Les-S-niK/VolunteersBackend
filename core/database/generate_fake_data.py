from core.database.models import User, Event, Link, UserEvent
from random import randint
from faker import Faker


fake = Faker()


async def fill_fake_users():
    for i in range(300):
        await User.add(
            full_name    = fake.name(),
            birth        = fake.date_of_birth(),
            city_id      = randint(100, 1000),
            passport     = f"{randint(1_000, 10_000)} {randint(100_000, 1_000_000)}",
            phone_number = f"+7{randint(1_000_000_000, 10_000_000_000)}",
            points       = randint(0, 100),
            password     = "".join([hex(randint(100_000_000, 1_000_000_000))[2:] for _ in range(5)]),
            telegram_id  = randint(100_000_000, 1_000_000_000) if randint(0, 4) else None,
        )


async def fill_fake_evens():
    for i in range(30):
        await Event.add(
            event_name = hex(randint(1024, 65536))[2:],
            date       = fake.date_between(),
        )


async def fill_fake_links():
    for i in range(3000):
        await Link.add(
            link       = fake.url(),
            is_checked = bool(randint(0, 4)),
            is_cool    = bool(randint(0, 4))
        )


async def fill_fake_users_events():
    users = await User.get_all()
    events = await Event.get_all()

    for user in users:
        if randint(0, 2):
            for event in events:
                if not randint(0, 3):
                    await UserEvent.add(
                        user_id  = user.id,
                        event_id = event.id
                    )
