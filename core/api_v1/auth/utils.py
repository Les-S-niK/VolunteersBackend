from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib.exceptions import UnknownHashError
from pydantic import SecretStr
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from config import TokenSettings, get_token_settings
from core.api_v1.auth.hashing import verify_password
from core.api_v1.auth.jwt_tokens import decode_access_token
from core.api_v1.auth.schemas import USER_ID_KEY, DecodedToken
from core.api_v1.http_exceptions import internal_server_error
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
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    return decoded_token


async def get_current_user(
    decoded_token: Annotated[DecodedToken, Depends(get_current_decoded_access_token)],
) -> User:
    user_id: int | None = decoded_token.decoded_payload.get(USER_ID_KEY)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    try:
        user_query_result: Result = (
            await CRUD.get(User).where(User.id == user_id).execute()
        )
    except SQLAlchemyError:
        raise internal_server_error
    user: User | None = user_query_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

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
