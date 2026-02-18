from typing import Any, Optional

from redis.asyncio import Redis


async def redis_create(
    redis: Redis, key: str, value: dict[str, Any], ttl: int = -1
) -> None:
    async with redis.client() as connection:
        await connection.hset(name=key, mapping=value)  ## type: ignore
        await connection.expire(name=key, time=ttl)


async def redis_delete(redis: Redis, key: str) -> None:
    async with redis.client() as connection:
        await connection.delete(key)


async def redis_read(redis: Redis, key: str) -> Optional[dict[str, Any]]:
    async with redis.client() as connection:
        data: dict[str, Any] = await connection.hgetall(key)  ## type: ignore
        return data if data else None
