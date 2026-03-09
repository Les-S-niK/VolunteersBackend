from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_VERSION: str = "0.1.1"


class ApiSettings(BaseSettings):
    HOST: Annotated[str, Field(default="127.0.0.1", title="Api IP host")] = "127.0.0.1"
    PORT: Annotated[int, Field(default=8080, title="Api port", ge=1, le=65535)] = 8080
    RELOAD: Annotated[
        bool,
        Field(
            default=False,
            title="Enable auto-reload",
            description="Fast API auto-reload for developing.",
        ),
    ] = False
    DEBUG: Annotated[
        bool,
        Field(
            default=False,
            title="Enable DEBUG mode",
            description="Enable Fast API debug mode.",
        ),
    ] = False
    SECURE: Annotated[
        bool,
        Field(
            default=True,
            title="Secure flag. (HTTPS)",
            description="Force HTTPS secure connection. (For cookies for example.)",
        ),
    ] = True

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="API_", extra="ignore"
    )


class TokenSettings(BaseSettings):
    REFRESH_EXPIRE_DAYS: Annotated[
        int,
        Field(default=30, title="Refresh token expiration time in days", ge=1, le=30),
    ] = 30
    ACCESS_EXPIRE_MINUTES: Annotated[
        int,
        Field(default=15, title="Access token expiration time in minutes", ge=1, le=60),
    ] = 15
    ALGORITHM: Annotated[
        str, Field(default="HS256", title="Access token algorithm type")
    ] = "HS256"
    ACCESS_SECRET_KEY: Annotated[
        SecretStr, Field(default=SecretStr(""), title="Token SECRET key", min_length=32)
    ] = SecretStr("")
    REFRESH_SECRET_KEY: Annotated[
        SecretStr, Field(default=SecretStr(""), title="Token SECRET key", min_length=32)
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
    HOST: Annotated[str, Field(default="127.0.0.1", title="Redis IP host")] = (
        "127.0.0.1"
    )
    PORT: Annotated[int, Field(default=6379, title="Redis port", ge=1, le=65535)] = 6379
    PASSWORD: Annotated[
        SecretStr,
        Field(default=SecretStr(""), title="Redis database password", min_length=6),
    ] = SecretStr("")

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="REDIS_", extra="ignore"
    )


class DBSettings(BaseSettings):
    HOST: Annotated[str, Field(default="127.0.0.1", title="DB IP host")] = "127.0.0.1"
    PORT: Annotated[int, Field(default=6379, title="DB port", ge=1, le=65535)] = 6379
    USER: Annotated[str, Field(default="", title="DB username")] = ""
    NAME: Annotated[str, Field(default="", title="DB name")] = ""
    PASSWORD: Annotated[
        SecretStr, Field(default=SecretStr(""), title="DB password", min_length=6)
    ] = SecretStr("")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_", extra="ignore")

    def get_db_url(self):
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD.get_secret_value()}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
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


@lru_cache
def get_db_settings() -> DBSettings:
    return DBSettings()
