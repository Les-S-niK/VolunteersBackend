from typing import Annotated

from fastapi import APIRouter, Depends

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import NotAuthorized
from core.api_v1.profile.schemas import UserProfile
from core.database.sqlalchemy.models import User

profile_router: APIRouter = APIRouter(prefix="/api/v1", tags=["Profile"])


@profile_router.get(
    path="/profiles/",
    description="Get user's profile.",
    responses={401: {"model": NotAuthorized, "description": "User not authorized."}},
)
async def profiles_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    return UserProfile(id=user.id, full_name=user.full_name, points=user.points)
