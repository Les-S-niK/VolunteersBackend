import asyncio

from core.database_export import exports


async def main() -> None:
    await exports.save_all_users_to_xlsx()
    await exports.save_all_events_to_xlsx()
    await exports.save_all_users_events_to_xlsx()
    await exports.save_all_links_to_xlsx()


asyncio.run(main=main())
