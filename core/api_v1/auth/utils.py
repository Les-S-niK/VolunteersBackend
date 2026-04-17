import datetime as dt
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib.exceptions import UnknownHashError
from pydantic import SecretStr
from redis.asyncio import Redis
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from config import TokenSettings, get_token_settings
from core.api_v1.auth.hashing import verify_password
from core.api_v1.auth.jwt_tokens import REFRESH_TOKEN_KEY, decode_access_token
from core.api_v1.auth.schemas import CITY_ID_KEY, JWT_ID_KEY, USER_ID_KEY, DecodedToken
from core.api_v1.http_exceptions import (
    internal_server_error,
    invalid_token_payload,
    not_authorized,
)
from core.database.redis import RedisCRUD, get_tokens_blacklist_redis
from core.database.redis.engine import get_refresh_redis
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import User

http_bearer: HTTPBearer = HTTPBearer()


async def get_current_decoded_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    token_settings: Annotated[TokenSettings, Depends(get_token_settings)],
) -> DecodedToken:
    access_token: str = credentials.credentials
    decoded_token: DecodedToken | None = decode_access_token(
        encoded_jwt=access_token,
        key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
        algorithms=[token_settings.ALGORITHM],
    )
    if not decoded_token:
        raise invalid_token_payload

    return decoded_token


def form_redis_user_id(city_id: int, user_id: int) -> str:
    """
    Form ID key to get user data from Redis database.
    Redis key structure: {city_iduser_id}

    Returns:
        str: formed ID.
    """
    return str(city_id).join(str(user_id))


async def get_current_user(
    decoded_token: Annotated[DecodedToken, Depends(get_current_decoded_access_token)],
    redis_blacklist_db: Annotated[Redis, Depends(get_tokens_blacklist_redis)],
) -> User:
    """
    Get current API user dependency.
    Validate access token and check it in the blacklist.

    Returns:
        User: If the token is valid and not in the blacklist.

    Raises:
        HTTPException with statuses 401 (Token is invalid) or 500 (Internal server error)
    """
    user_id: int | None = decoded_token.decoded_payload.get(USER_ID_KEY)
    city_id: int | None = decoded_token.decoded_payload.get(CITY_ID_KEY)
    if not user_id or not city_id:
        raise invalid_token_payload

    jwt_index: UUID | None = decoded_token.decoded_payload.get(JWT_ID_KEY)
    if not jwt_index:
        raise invalid_token_payload

    try:
        async with RedisCRUD(redis_blacklist_db) as redis:
            blacklist_access_token: str | None = await redis.read(key=str(jwt_index))
    except Exception:
        raise internal_server_error

    if blacklist_access_token:
        raise not_authorized
    try:
        user_query_result: Result = (
            await CRUD.get(User)
            .where(User.id == user_id, User.city_id == city_id)
            .execute()
        )
    except SQLAlchemyError:
        raise internal_server_error
    user: User | None = user_query_result.scalar_one_or_none()

    if not user:
        raise not_authorized
    return user


def try_verify_password(
    plain_password: SecretStr, hashed_password: str, exception: Exception
) -> bool:
    try:
        if not verify_password(plain_password.get_secret_value(), hashed_password):
            raise exception
    except UnknownHashError:
        raise exception

    return True


async def user_logout(
    user: User,
    response: Response,
    redis_blacklist_db: Redis,
    redis_refresh_db: Redis,
    decoded_token: DecodedToken,
) -> Response:
    try:
        async with RedisCRUD(redis_refresh_db) as redis_refresh:
            await redis_refresh.delete(
                key=form_redis_user_id(user_id=user.id, city_id=user.city_id)
            )
    except Exception:
        raise internal_server_error

    response.delete_cookie(REFRESH_TOKEN_KEY)
    access_ttl: int = int(
        (
            decoded_token.expiration_date - dt.datetime.now(dt.timezone.utc)
        ).total_seconds()
    )
    jwt_index: UUID | None = decoded_token.decoded_payload.get(JWT_ID_KEY)

    if not jwt_index or access_ttl < 0:
        raise invalid_token_payload

    default_blacklist_value: str = "blacklist"
    try:
        async with RedisCRUD(redis_blacklist_db) as redis_blacklist:
            ## We do not need to store any value for the jwt index key
            ## because the /login/ endpoint will check only if jwt index in the blacklist.
            await redis_blacklist.create(
                key=str(jwt_index),
                value=default_blacklist_value,
                ttl_seconds=access_ttl,
            )
    except Exception:
        raise internal_server_error

    response.status_code = status.HTTP_204_NO_CONTENT
    return response
