from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from pydantic import HttpUrl

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import Forbidden, InternalServerError, NotFoundError
from core.api_v1.links.schemas import LinkToVerifyModel, VerifiedLinkResult
from core.database.sqlalchemy.models import Link, User

links_router: APIRouter = APIRouter(prefix="/api/v1/links", tags=["Links"])


@links_router.patch(
    path="/after_verification/",
    description='Set a new value in the "is_prohibited" link field after link verification.',
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Link status was patched."},
        status.HTTP_403_FORBIDDEN: {"model": Forbidden},
        status.HTTP_404_NOT_FOUND: {"model": NotFoundError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": InternalServerError,
        },
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def after_verification_handler(
    link: Annotated[VerifiedLinkResult, Body()],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """
    Patch links.is_prohibited field in the database.
    Only user who took a link can patch the field.
    """
    found_link: Link | None = await Link.get_by_link(link=str(link.link))
    if not found_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    if found_link.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not access this link.",
        )

    update_result: bool = await Link.update(
        id=found_link.id, is_prohibited=link.is_prohibited
    )
    if not update_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@links_router.patch(
    path="/first_unverified/",
    description="Get the first unverified link with max priority from the database. Update a record in the database. (Set the user who took the link in user_id field.)",
    response_model=LinkToVerifyModel,
    responses={
        status.HTTP_200_OK: {
            "model": LinkToVerifyModel,
            "description": "Successfully got a link from the DB.",
        },
        status.HTTP_204_NO_CONTENT: {"description": "No content"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": InternalServerError,
        },
    },
)
async def first_unverified_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> LinkToVerifyModel | Response:
    """
    Get the first unverified link with max priority from the database and return it.
    Patch the links.user_id field by user's ID who took it.
    """
    first_unverified_link: Link | None = await Link.get_first_priority_unverified()
    if not first_unverified_link:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    update_result: bool = await Link.update(
        id=first_unverified_link.id, user_id=user.id
    )
    if not update_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return LinkToVerifyModel(link=HttpUrl(first_unverified_link.link))
