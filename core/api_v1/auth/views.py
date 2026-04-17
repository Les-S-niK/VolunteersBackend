import datetime as dt
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_204_NO_CONTENT

from config import ApiSettings, TokenSettings, get_api_settings, get_token_settings
from core.api_v1.auth.hashing import hash_password, verify_password
from core.api_v1.auth.jwt_tokens import (
    REFRESH_TOKEN_KEY,
    create_tokens_pair,
    decode_access_token,
)
from core.api_v1.auth.schemas import (
    CITY_ID_KEY,
    JWT_ID_KEY,
    USER_ID_KEY,
    ChangePasswordModel,
    DecodedToken,
    EncodedToken,
    EncodedTokensPair,
    TokenTypesEnum,
    UserAuth,
)
from core.api_v1.auth.utils import (
    form_redis_user_id,
    get_current_decoded_access_token,
    get_current_user,
    try_verify_password,
    user_logout,
)
from core.api_v1.error_schemas import (
    InternalServerError,
    NotAuthorized,
    TooManyRequestsError,
)
from core.api_v1.http_exceptions import (
    forbidden,
    internal_server_error,
    invalid_token_payload,
    not_authorized,
)
from core.database.redis import RedisCRUD, get_refresh_redis, get_tokens_blacklist_redis
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import User

auth_router: APIRouter = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authenticate"],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": TooManyRequestsError},
        status.HTTP_401_UNAUTHORIZED: {
            "model": NotAuthorized,
            "description": "Not authorized",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)


SECONDS_IN_DAY: int = 86400


@auth_router.post(
    path="/refresh/",
    description="Get access token by provided refresh token in the cookies.",
    responses={
        status.HTTP_200_OK: {"model": EncodedToken},
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
    refresh_token: str | None = request.cookies.get(REFRESH_TOKEN_KEY)
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
    city_id: int | None = payload.decoded_payload.get(CITY_ID_KEY)

    if not user_id or not city_id:
        raise invalid_token_exception

    try:
        async with RedisCRUD(redis_db) as redis:
            token_hash: str | None = await redis.read(
                form_redis_user_id(city_id=city_id, user_id=user_id)
            )
    except Exception:
        raise internal_server_error

    if not token_hash or not verify_password(refresh_token, token_hash):
        raise invalid_token_exception

    tokens_pair: EncodedTokensPair = create_tokens_pair(
        data={JWT_ID_KEY: str(uuid4()), CITY_ID_KEY: city_id, USER_ID_KEY: user_id},
        access_expires_delta=token_settings.access_token_expire,
        access_key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
        refresh_expires_delta=token_settings.refresh_token_expire,
        refresh_key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithm=token_settings.ALGORITHM,
    )

    refresh_ttl: int = int(token_settings.refresh_token_expire.total_seconds())
    try:
        async with RedisCRUD(redis_db) as redis:
            await redis.create(
                key=form_redis_user_id(city_id=city_id, user_id=user_id),
                value=hash_password(tokens_pair.refresh_token),
                ttl_seconds=refresh_ttl,
            )
    except Exception:
        raise internal_server_error

    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
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
    Get user's login data (user_id, city_id, password), validate it and generate a tokens pair. (Access and refresh tokens)
    Set refresh token in the "refresh" http only cookies field.

    Returns:
        EncodedToken: encoded JWT access token.
    """
    try:
        statement_result: Result = (
            await CRUD.get(User)
            .where(User.id == user_auth.user_id, User.city_id == user_auth.city_id)
            .execute()
        )
    except SQLAlchemyError:
        raise internal_server_error
    user: User | None = statement_result.scalar_one_or_none()

    if not user:
        raise not_authorized
    try_verify_password(user_auth.password, user.password, not_authorized)

    tokens_pair: EncodedTokensPair = create_tokens_pair(
        data={
            JWT_ID_KEY: str(uuid4()),
            CITY_ID_KEY: user_auth.city_id,
            USER_ID_KEY: user_auth.user_id,
        },
        access_expires_delta=token_settings.access_token_expire,
        access_key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
        refresh_expires_delta=token_settings.refresh_token_expire,
        refresh_key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithm=token_settings.ALGORITHM,
    )
    refresh_ttl: int = int(token_settings.refresh_token_expire.total_seconds())
    try:
        async with RedisCRUD(redis_db) as redis:
            await redis.create(
                key=form_redis_user_id(
                    city_id=user_auth.city_id, user_id=user_auth.user_id
                ),
                value=hash_password(tokens_pair.refresh_token),
                ttl_seconds=refresh_ttl,
            )
    except Exception:
        raise internal_server_error

    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
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


@auth_router.delete(
    path="/logout/",
    description="Logout from the user's account.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "User logged out successfully."},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_handler(
    response: Response,
    user: Annotated[User, Depends(get_current_user)],
    redis_blacklist_db: Annotated[Redis, Depends(get_tokens_blacklist_redis)],
    redis_refresh_db: Annotated[Redis, Depends(get_refresh_redis)],
    decoded_token: Annotated[DecodedToken, Depends(get_current_decoded_access_token)],
) -> Response:
    return await user_logout(
        user=user,
        response=response,
        redis_blacklist_db=redis_blacklist_db,
        redis_refresh_db=redis_refresh_db,
        decoded_token=decoded_token,
    )


@auth_router.patch(
    path="/change_password/",
    description="Change user's password to a new one.",
    status_code=HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Password has changed successfully."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User can not access this resource."
        },
    },
)
async def change_password_handler(
    response: Response,
    user: Annotated[User, Depends(get_current_user)],
    redis_blacklist_db: Annotated[Redis, Depends(get_tokens_blacklist_redis)],
    redis_refresh_db: Annotated[Redis, Depends(get_refresh_redis)],
    decoded_token: Annotated[DecodedToken, Depends(get_current_decoded_access_token)],
    password_data: Annotated[ChangePasswordModel, Body(title="User's password data.")],
) -> Response:
    async with CRUD() as session:
        try:
            user_result: Result = (
                await CRUD.get(User, session=session)
                .where(User.id == user.id)
                .with_for_update()
                .execute()
            )
            user_from_db: User | None = user_result.scalar_one_or_none()
        except Exception:
            await session.rollback()
            raise internal_server_error

        if not user_from_db or not verify_password(
            password_data.old_password.get_secret_value(), user.password
        ):
            raise forbidden

        try:
            await (
                CRUD.update(User, session=session)
                .where(User.id == user_from_db.id)
                .values(
                    password=hash_password(
                        password_data.new_password.get_secret_value()
                    )
                )
                .execute()
            )
        except Exception:
            await session.rollback()
            raise internal_server_error

        await user_logout(
            user=user,
            response=response,
            redis_blacklist_db=redis_blacklist_db,
            redis_refresh_db=redis_refresh_db,
            decoded_token=decoded_token,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
