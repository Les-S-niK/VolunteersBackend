from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    HOST: Annotated[str, Field(title="Api IP host")] = "0.0.0.0"
    PORT: Annotated[int, Field(title="Api port", ge=1, le=65535)] = 8080
    RELOAD: Annotated[
        bool,
        Field(
            title="Enable auto-reload",
            description="Fast API auto-reload for developing.",
        ),
    ] = False
    DEBUG: Annotated[
        bool,
        Field(title="Enable DEBUG mode", description="Enable Fast API debug mode."),
    ] = False

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="API_", extra="ignore"
    )


class TokenSettings(BaseSettings):
    TYPE: Annotated[str, Field(title="Access token type")] = "Bearer"
    REFRESH_EXPIRE_DAYS: Annotated[
        int, Field(title="Refresh token expiration time in days", ge=1, le=30)
    ] = 30
    ACCESS_EXPIRE_MINUTES: Annotated[
        int, Field(title="Access token expiration time in days", ge=1, le=60)
    ] = 15
    ALGORITHM: Annotated[str, Field(title="Access token algorithm type")] = "HS256"
    ACCESS_SECRET_KEY: Annotated[
        SecretStr, Field(title="Token SECRET key", min_length=32)
    ] = SecretStr("")
    REFRESH_SECRET_KEY: Annotated[
        SecretStr, Field(title="Token SECRET key", min_length=32)
    ] = SecretStr("")

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_EXPIRE_MINUTES)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(days=self.REFRESH_EXPIRE_DAYS)

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="TOKEN_", extra="ignore"
    )


class RedisSettings(BaseSettings):
    HOST: Annotated[str, Field(title="Redis IP host")] = "0.0.0.0"
    PORT: Annotated[int, Field(title="Redis port", ge=1, le=65535)] = 6379
    PASSWORD: Annotated[
        SecretStr, Field(title="Redis database password", min_length=6)
    ] = SecretStr("")

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="REDIS_", extra="ignore"
    )


@lru_cache
def get_token_settings() -> TokenSettings:
    return TokenSettings()


@lru_cache
def get_api_settings() -> ApiSettings:
    return ApiSettings()


@lru_cache
def get_redis_settings() -> RedisSettings:
    return RedisSettings()
