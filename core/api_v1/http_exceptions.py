from fastapi import status
from fastapi.exceptions import HTTPException

internal_server_error: HTTPException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error",
)

invalid_token_payload: HTTPException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload."
)

not_authorized: HTTPException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
)
