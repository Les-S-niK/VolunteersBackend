from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from pydantic import SecretStr
from redis.asyncio import Redis

from config import ApiSettings, TokenSettings, get_api_settings, get_token_settings
from core.api_v1.auth.hashing import hash_password, verify_password
from core.api_v1.auth.jwt_tokens import create_tokens_pair, decode_access_token
from core.api_v1.auth.schemas import (
    USER_ID_KEY,
    DecodedToken,
    EncodedToken,
    EncodedTokensPair,
    TokenTypesEnum,
    UserAuth,
)
from core.api_v1.auth.utils import try_verify_password
from core.api_v1.error_schemas import InvalidRefreshTokenError, NotAuthorized
from core.database.redis import RedisCRUD, get_refresh_redis
from core.database.sqlalchemy.models import User

auth_router: APIRouter = APIRouter(prefix="/api/v1/auth", tags=["Authenticate"])


SECONDS_IN_DAY: int = 86400


@auth_router.post(
    path="/refresh/",
    description="Get access token by provided refresh token in the cookies.",
    responses={
        status.HTTP_200_OK: {"model": EncodedToken},
        status.HTTP_401_UNAUTHORIZED: {
            "model": InvalidRefreshTokenError,
            "detail": "Invalid refresh token.",
        },
    },
)
async def refresh_handler(
    request: Request,
    response: Response,
    token_settings: Annotated[TokenSettings, Depends(get_token_settings)],
    api_settings: Annotated[ApiSettings, Depends(get_api_settings)],
    redis_db: Annotated[Redis, Depends(get_refresh_redis)],
) -> EncodedToken:
    """
    Get a refresh token from the cookies and generate a new tokens pair. (Refresh and access tokens)
    Save a refresh token in the Redis DB.

    Returns:
        EncodedToken: encoded JWT access token.
    """
    refresh_token: str | None = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=401, detail="Can't find refresh token in cookies."
        )

    invalid_token_exception: HTTPException = HTTPException(
        status_code=401, detail="Invalid refresh token."
    )
    payload: DecodedToken | None = decode_access_token(
        encoded_jwt=refresh_token,
        key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithms=[token_settings.ALGORITHM],
    )
    if not payload:
        raise invalid_token_exception

    user_id: int | None = payload.decoded_payload.get(USER_ID_KEY)
    if not user_id:
        raise invalid_token_exception

    async with RedisCRUD(redis_db) as redis:
        token_hash: str | None = await redis.read(str(user_id))

    if not token_hash or not verify_password(refresh_token, token_hash):
        raise invalid_token_exception

    tokens_pair: EncodedTokensPair = create_tokens_pair(
        data={USER_ID_KEY: user_id},
        access_expires_delta=token_settings.access_token_expire,
        access_key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
        refresh_expires_delta=token_settings.refresh_token_expire,
        refresh_key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithm=token_settings.ALGORITHM,
    )

    refresh_ttl: int = int(token_settings.refresh_token_expire.total_seconds())
    async with RedisCRUD(redis_db) as redis:
        await redis.create(
            key=str(user_id),
            value=hash_password(tokens_pair.refresh_token),
            ttl_seconds=refresh_ttl,
        )

    response.set_cookie(
        key="refresh_token",
        value=tokens_pair.refresh_token,
        httponly=True,
        secure=api_settings.SECURE,
        samesite="strict",
        max_age=refresh_ttl,
        path="/api/v1/auth/",
    )

    return EncodedToken(
        token=tokens_pair.access_token, token_type=TokenTypesEnum.access
    )


@auth_router.post(
    path="/login/",
    description="Create access and refresh tokens based on user data.",
    responses={
        status.HTTP_200_OK: {"model": EncodedToken},
        status.HTTP_401_UNAUTHORIZED: {
            "model": NotAuthorized,
            "description": "Not authorized",
        },
    },
)
async def login_handler(
    response: Response,
    user_auth: Annotated[UserAuth, Body(title="User auth model.")],
    token_settings: Annotated[TokenSettings, Depends(get_token_settings)],
    api_settings: Annotated[ApiSettings, Depends(get_api_settings)],
    redis_db: Annotated[Redis, Depends(get_refresh_redis)],
) -> EncodedToken:
    """
    Get user's login data (user_id, password), validate it and generate a tokens pair. (Access and refresh tokens)
    Set refresh token in the "refresh" httponly cookies field.

    Returns:
        EncodedToken: encoded JWT access token.
    """
    user_id: int = user_auth.user_id
    user_password: SecretStr = user_auth.password

    user: User | None = await User.get_by_id(user_id)

    not_found_exception: HTTPException = HTTPException(
        status_code=401, detail="Not authorized"
    )
    if not user:
        raise not_found_exception
    try_verify_password(user_password, user.password, not_found_exception)

    tokens_pair: EncodedTokensPair = create_tokens_pair(
        data={USER_ID_KEY: user_id},
        access_expires_delta=token_settings.access_token_expire,
        access_key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
        refresh_expires_delta=token_settings.refresh_token_expire,
        refresh_key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithm=token_settings.ALGORITHM,
    )

    refresh_ttl: int = int(token_settings.refresh_token_expire.total_seconds())
    async with RedisCRUD(redis_db) as redis:
        await redis.create(
            key=str(user_id),
            value=hash_password(tokens_pair.refresh_token),
            ttl_seconds=refresh_ttl,
        )

    response.set_cookie(
        key="refresh_token",
        value=tokens_pair.refresh_token,
        httponly=True,
        secure=api_settings.SECURE,
        samesite="strict",
        max_age=refresh_ttl,
        path="/api/v1/auth/",
    )

    return EncodedToken(
        token=tokens_pair.access_token, token_type=TokenTypesEnum.access
    )
