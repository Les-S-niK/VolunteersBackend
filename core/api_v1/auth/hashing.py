from pwdlib import PasswordHash


hasher: PasswordHash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies given passwords and returns the result.
    Args:
        plain_password: str - raw password in text to verify with hash.
        hashed_password: str - hashed password.

    Returns:
        bool - True if verification is successful.
    """
    return hasher.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    """Hashes the given password and returns it's hash with dynamic salt.
    Args:
        plain_password: str - raw password text to hash.

    Returns:
        str - password hash with dynamic salt.
    """
    return hasher.hash(plain_password)
