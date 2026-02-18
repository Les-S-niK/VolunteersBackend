from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import SecretStr
from redis.asyncio import Redis

from config import TokenSettings, get_token_settings
from core.api_v1.auth.hashing import hash_password
from core.api_v1.auth.jwt_tokens import create_access_token
from core.api_v1.auth.schemas import USER_ID_KEY, EncodedToken, UserAuth
from core.database.redis import redis_create, refresh_db_name
from core.database.redis.engine import get_redis_client

auth_router: APIRouter = APIRouter(prefix="/api/v1/auth", tags=["Authenticate", "User"])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="create_tokens", description="Create tokens handler"
)


@auth_router.post(
    path="/create_tokens/",
    description="Create access and refresh tokens based on user data.",
)
async def create_tokens_handler(
    response: Response,
    user_auth: Annotated[UserAuth, Body(title="User auth model.")],
    token_settings: Annotated[TokenSettings, Depends(get_token_settings)],
) -> EncodedToken:
    SECONDS_IN_DAY: int = 86400
    user_id: str = str(user_auth.user_id)
    user_password: SecretStr = user_auth.password

    ## TODO: Send GET requests to the database to check if user phone_number inside. Make password verification.
    user_data_valid: bool = True
    hashed_user_password: str = hash_password(str(user_password))

    if not user_data_valid:
        ...

    data_to_encode: dict[str, Any] = {USER_ID_KEY: user_id}

    acces_token: EncodedToken = EncodedToken(
        encoded_payload=create_access_token(
            data=data_to_encode,
            expires_delta=token_settings.access_token_expire,
            key=token_settings.ACCESS_SECRET_KEY.get_secret_value(),
            algorithm=token_settings.ALGORITHM,
        ),
        token_type=token_settings.TYPE,
    )
    refresh_token: str = create_access_token(
        data=data_to_encode,
        expires_delta=token_settings.refresh_token_expire,
        key=token_settings.REFRESH_SECRET_KEY.get_secret_value(),
        algorithm=token_settings.ALGORITHM,
    )

    redis_db: Redis = get_redis_client(db_name=refresh_db_name)
    redis_value_to_write: dict[str, str] = {
        user_id: hash_password(refresh_token),
    }
    await redis_create(
        redis=redis_db,
        key="refresh",
        value=redis_value_to_write,
        ttl=token_settings.REFRESH_EXPIRE_DAYS * SECONDS_IN_DAY,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return acces_token
