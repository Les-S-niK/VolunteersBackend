import asyncio

from core.database.sqlalchemy.generate_fake_data import recreate_db


async def main() -> None:
    await recreate_db()


if __name__ == "__main__":
    asyncio.run(main=main())
