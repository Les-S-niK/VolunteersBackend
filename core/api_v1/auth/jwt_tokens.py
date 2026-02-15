from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidKeyError

from core.api_v1.auth.schemas import DecodedToken


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta, key: str, algorithm: str
) -> str:
    """Creates access token from provided data with {now + expires_delta} lifespan.
    Args:
        data: dict[str, Any] - provided data to encode in jwt.
        expires_delta: timedelta - token lifespan time.
        key: str - Secret token key.
        algorithm: str - Token algorithm.

    Returns:
        Access jwt token.
    """
    if not expires_delta:
        raise InvalidKeyError("Invalid expiration delta time.")

    payload_to_encode: dict[str, Any] = data.copy()
    expires: datetime = datetime.now(timezone.utc) + expires_delta
    payload_to_encode.update({"exp": expires})

    return jwt.encode(payload=payload_to_encode, key=key, algorithm=algorithm)


def decode_access_token(
    encoded_jwt: str, key: str, algorithms: list[str]
) -> DecodedToken:
    """Decodes given jwt token and returns it's data and it's expiration time.

    Args:
        encoded_jwt: str - encoded jwt token.
        key: str - secret token key.
        algorithms: list[str] - list of token algorithms.

    Returns:
        DecodedToken - Token data and it's expiration time.
    """
    decoded_payload: dict[str, Any] = jwt.decode(
        jwt=encoded_jwt, key=key, algorithms=algorithms
    )

    expires: Optional[datetime] = decoded_payload.get("exp")
    if not expires:
        raise ExpiredSignatureError(
            "Can't find expired signature in the token payload."
        )

    return DecodedToken(decoded_payload=decoded_payload, expiration_date=expires)
