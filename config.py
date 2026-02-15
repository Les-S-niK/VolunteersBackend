from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from pydantic import Field
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
    EXPIRE_DAYS: Annotated[
        int, Field(title="Token expiration time in days", ge=1, le=30)
    ] = 5
    SECRET_KEY: Annotated[str, Field(title="Token SECRET key", min_length=32)] = ""
    ALGORITHM: Annotated[str, Field(title="Access token algorithm type")] = "HS256"

    @property
    def token_expire(self) -> timedelta:
        return timedelta(days=self.EXPIRE_DAYS)

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="TOKEN_", extra="ignore"
    )


@lru_cache
def get_token_settings() -> TokenSettings:
    return TokenSettings()


@lru_cache
def get_api_settings() -> ApiSettings:
    return ApiSettings()
