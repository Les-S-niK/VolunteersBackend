from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from pydantic import SecretStr
from redis.asyncio import Redis

from config import TokenSettings, get_token_settings
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
from core.api_v1.error_schemas import InvalidRefreshTokenError, NotFoundError
from core.database.redis import get_refresh_redis_client, redis_create, redis_read
from core.database.sqlalchemy.models import User

auth_router: APIRouter = APIRouter(prefix="/api/v1/auth", tags=["Authenticate"])


SECONDS_IN_DAY: int = 86400


@auth_router.get(
    path="/refresh/",
    description="Get access token by provided refresh token in the cookies.",
    responses={
        401: {"model": InvalidRefreshTokenError, "detail": "Invalid refresh token."}
    },
)
async def refresh_handler(
    request: Request,
    response: Response,
    token_settings: Annotated[TokenSettings, Depends(get_token_settings)],
    redis_client: Annotated[Redis, Depends(get_refresh_redis_client)],
) -> EncodedToken:
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

    token_hash: str | None = await redis_read(
        redis=redis_client, field="refresh", key=str(user_id)
    )
    if not token_hash or not verify_password(refresh_token, token_hash):
        response.delete_cookie("refresh_token")
        raise invalid_token_exception

    tokens_pair: EncodedTokensPair = create_tokens_pair(
        data={USER_ID_KEY: user_id},
        access_expires_delta=token_settings.access_token_expire,
        access_key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
        refresh_expires_delta=token_settings.refresh_token_expire,
        refresh_key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithm=token_settings.ALGORITHM,
    )

    redis_value_to_write: dict[str, str] = {
        str(user_id): hash_password(tokens_pair.refresh_token),
    }

    refresh_ttl: int = token_settings.REFRESH_EXPIRE_DAYS * SECONDS_IN_DAY
    await redis_create(
        redis=redis_client,
        key="refresh",
        value=redis_value_to_write,
        ttl=refresh_ttl,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens_pair.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=refresh_ttl,
    )

    return EncodedToken(
        token=tokens_pair.access_token, token_type=TokenTypesEnum.access
    )


@auth_router.post(
    path="/login/",
    description="Create access and refresh tokens based on user data.",
    responses={404: {"model": NotFoundError, "description": "Not found"}},
)
async def login_handler(
    response: Response,
    user_auth: Annotated[UserAuth, Body(title="User auth model.")],
    redis_client: Annotated[Redis, Depends(get_refresh_redis_client)],
    token_settings: Annotated[TokenSettings, Depends(get_token_settings)],
) -> EncodedToken:
    user_id: int = user_auth.user_id
    user_password: SecretStr = user_auth.password

    user: User | None = await User.get_by_id(user_id)

    not_found_exception: HTTPException = HTTPException(
        status_code=404, detail="User not found."
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
    redis_value_to_write: dict[str, str] = {
        str(user_id): hash_password(tokens_pair.refresh_token),
    }

    refresh_ttl: int = token_settings.REFRESH_EXPIRE_DAYS * SECONDS_IN_DAY
    await redis_create(
        redis=redis_client,
        key="refresh",
        value=redis_value_to_write,
        ttl=refresh_ttl,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens_pair.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=refresh_ttl,
    )

    return EncodedToken(
        token=tokens_pair.access_token, token_type=TokenTypesEnum.access
    )
