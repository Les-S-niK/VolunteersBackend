from typing import Self

from redis.asyncio import Redis
from redis.exceptions import ConnectionError


class RedisSessionNotInitializedError(ConnectionError):
    def __init__(self, operation: str) -> None:
        super().__init__(
            f"Can't perform {operation} operation. Redis session not initilized."
        )


class RedisCRUD:
    def __init__(self, redis: Redis) -> None:
        self.redis: Redis = redis
        self.session: Redis | None = None

    async def __aenter__(self) -> Self:
        self.session = await self.redis.client()
        return self

    async def __aexit__(self, *_) -> None:
        if self.session:
            await self.session.close()

    async def create(
        self, key: str, value: str, ttl_seconds: int | None = None
    ) -> None:
        if not self.session:
            raise RedisSessionNotInitializedError(operation="create")

        if not ttl_seconds:
            await self.session.set(name=key, value=value)
        else:
            await self.session.setex(name=key, time=ttl_seconds, value=value)

    async def delete(self, key: str) -> None:
        if not self.session:
            raise RedisSessionNotInitializedError(operation="delete")
        await self.session.delete(key)

    async def read(self, key: str) -> str | None:
        if not self.session:
            raise RedisSessionNotInitializedError(operation="read")
        data: bytes | None = await self.session.get(key)

        if data is None:
            return None
        return data.decode()
