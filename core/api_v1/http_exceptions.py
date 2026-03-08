from fastapi import status
from fastapi.exceptions import HTTPException

internal_server_error: HTTPException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error",
)
