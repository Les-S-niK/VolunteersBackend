
from typing import Annotated

from fastapi import APIRouter, Body



sign_in_router: APIRouter = APIRouter(
    prefix="/api/v1/sign_in",
    tags=["Sign In", "User"]
)


