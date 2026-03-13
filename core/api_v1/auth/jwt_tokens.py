from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidKeyError

from core.api_v1.auth.schemas import DecodedToken, EncodedTokensPair


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
) -> DecodedToken | None:
    """Decodes given jwt token and returns it's data and it's expiration time.

    Args:
        encoded_jwt: str - encoded jwt token.
        key: str - secret token key.
        algorithms: list[str] - list of token algorithms.

    Returns:
        DecodedToken - Token data and it's expiration time.
    """
    try: 
        decoded_payload: dict[str, Any] = jwt.decode(
            jwt=encoded_jwt, key=key, algorithms=algorithms
        )
    except jwt.PyJWTError:
        return None

    expires: datetime | None = decoded_payload.get("exp")
    if not expires:
        return None

    return DecodedToken(decoded_payload=decoded_payload, expiration_date=expires)


def create_tokens_pair(
    data: dict[str, Any],
    access_expires_delta: timedelta,
    refresh_expires_delta: timedelta,
    access_key: str,
    refresh_key: str,
    algorithm: str,
) -> EncodedTokensPair:
    return EncodedTokensPair(
        access_token=create_access_token(
            data=data,
            expires_delta=access_expires_delta,
            key=access_key,
            algorithm=algorithm,
        ),
        refresh_token=create_access_token(
            data=data,
            expires_delta=refresh_expires_delta,
            key=refresh_key,
            algorithm=algorithm,
        ),
    )
