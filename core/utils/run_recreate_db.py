import asyncio

from core.database.sqlalchemy.generate_fake_data import init_db, drop_db


async def main() -> None:
    await init_db()
    await drop_db()


if __name__ == "__main__":
    asyncio.run(main=main())
