from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from jwt.exceptions import InvalidKeyError, InvalidTokenError

from config import TOKEN_ALGORITHM, TOKEN_EXPIRE, TOKEN_SECRET_KEY
from core.api_v1.auth.schemas import DecodedToken


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = TOKEN_EXPIRE
) -> str:
    """Creates access token from provided data with {now + expires_delta} lifespan.
    Args:
        data: dict[str, Any] - provided data to encode in jwt.
        expires_delta: Optional[timedelta] - token lifespan time.

    Returns:
        Access jwt token.
    """
    if not expires_delta:
        raise InvalidKeyError("Invalid expiration delta time.")

    payload_to_encode: dict[str, Any] = data.copy()
    expires: datetime = datetime.now(timezone.utc) + expires_delta
    payload_to_encode.update({"exp": expires})

    return jwt.encode(
        payload=payload_to_encode, key=TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM
    )


def decode_access_token(encoded_jwt: str) -> DecodedToken:
    """Decodes given jwt token and returns it's data and it's expiration time.

    Args:
        encoded_jwt: str - encoded jwt token.

    Returns:
        DecodedToken - Token data and it's expiration time.

    """
    decoded_payload: dict[str, Any] = jwt.decode(
        jwt=encoded_jwt, key=TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM]
    )
    expires: Optional[datetime] = decoded_payload.get("exp")
    if not expires:
        raise InvalidTokenError("Can't find expiring signature.")

    return DecodedToken(decoded_payload=decoded_payload, expiration_date=expires)
