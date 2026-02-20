from pwdlib.exceptions import UnknownHashError
from pydantic import SecretStr

from core.api_v1.auth.hashing import verify_password


def try_verify_password(
    plain_password: SecretStr, hashed_password: str, exception: Exception
) -> bool:
    try:
        if not verify_password(plain_password.get_secret_value(), hashed_password):
            raise exception
    except UnknownHashError:
        raise exception

    return True
