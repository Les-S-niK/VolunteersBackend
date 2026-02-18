from functools import lru_cache

from redis.asyncio import Redis

from config import RedisSettings, get_redis_settings

redis_settings: RedisSettings = get_redis_settings()
refresh_db_name: int = 1


@lru_cache
def get_redis_client(db_name: str) -> Redis:
    return Redis(
        host=redis_settings.HOST,
        port=redis_settings.PORT,
        password=redis_settings.PASSWORD.get_secret_value(),
        db=db_name,
    )
