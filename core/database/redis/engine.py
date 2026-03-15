from enum import StrEnum
from functools import lru_cache

from redis.asyncio import Redis

from config import RedisSettings, get_redis_settings

redis_settings: RedisSettings = get_redis_settings()


class RedisNamesEnum(StrEnum):
    REFRESH = "1"
    BLACKLIST_ACCESS = "2"


@lru_cache
def get_redis(db_name: RedisNamesEnum) -> Redis:
    return Redis(
        host=redis_settings.HOST,
        port=redis_settings.PORT,
        password=redis_settings.PASSWORD.get_secret_value(),
        db=db_name,
    )


def get_tokens_blacklist_redis() -> Redis:
    return get_redis(RedisNamesEnum.REFRESH)


def get_refresh_redis() -> Redis:
    return get_redis(RedisNamesEnum.BLACKLIST_ACCESS)
