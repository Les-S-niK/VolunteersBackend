from typing import Annotated, Any

from fastapi import APIRouter, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import SecretStr

from config import TOKEN_TYPE
from core.api_v1.auth.hashing import hash_password
from core.api_v1.auth.jwt_tokens import create_access_token
from core.api_v1.auth.schemas import PHONE_NUMBER_FIELD, EncodedToken, UserAuth

auth_router: APIRouter = APIRouter(prefix="/api/v1/auth", tags=["Authenticate", "User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="create_token")


@auth_router.post(
    path="/create_token/", description="Create access token based on user data."
)
async def create_token_handler(
    user_auth: Annotated[UserAuth, Body(title="User auth model.")],
) -> EncodedToken:
    user_phone_number: str = str(user_auth.phone_number)
    user_password: SecretStr = user_auth.password

    ## TODO: Send get requests to the database to check if user phone_number in it. Make password verification.
    user_data_valid: bool = True
    hashed_user_password: str = hash_password(str(user_password))

    if not user_data_valid:
        ...

    data_to_encode: dict[str, Any] = {PHONE_NUMBER_FIELD: user_phone_number}

    return EncodedToken(
        encoded_payload=create_access_token(data=data_to_encode), token_type=TOKEN_TYPE
    )
