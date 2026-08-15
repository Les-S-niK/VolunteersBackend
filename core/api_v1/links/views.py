from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from config import ApiSettings, get_api_settings
from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import (
    Forbidden,
    InternalServerError,
    NotAuthorized,
    NotFoundError,
    TooManyRequestsError,
)
from core.api_v1.http_exceptions import internal_server_error
from core.api_v1.links.schemas import LinkToVerifyModel, VerifiedLinkResult
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Link, User

links_router: APIRouter = APIRouter(
    prefix="/api/v1/links",
    tags=["Links"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": NotAuthorized},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": TooManyRequestsError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)


@links_router.patch(
    path="/after_verification/",
    description='Set a new value in the "is_prohibited" link field after link verification.',
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Link status was patched."},
        status.HTTP_403_FORBIDDEN: {"model": Forbidden},
        status.HTTP_404_NOT_FOUND: {"model": NotFoundError},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def after_verification_handler(
    link: Annotated[VerifiedLinkResult, Body()],
    user: Annotated[User, Depends(get_current_user)],
    api_settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> Response:
    """
    Patch links.is_prohibited field in the database.
    Only user who took a link can patch the field.
    Add 1 point to user if is_prohibited is true and ENABLE_USER_REWARD enabled.
    """
    async with CRUD() as session:
        try:
            link_query_result: Result = (
                await CRUD.get(Link, session=session)
                .where(Link.link == str(link.link), Link.is_prohibited.is_(None))
                .with_for_update()
                .execute()
            )
            found_link: Link | None = link_query_result.scalar_one_or_none()
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        if not found_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found or checked already.",
            )
        if found_link.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can not access this link.",
            )

        try:
            await (
                CRUD.update(Link, session=session)
                .where(Link.id == found_link.id)
                .values(
                    is_prohibited=link.is_prohibited,
                    violation_type=link.violation_type,
                    content_type=link.content_type,
                )
                .execute()
            )
            if found_link.is_prohibited and api_settings.ENABLE_USER_REWARD:
                await (
                    CRUD.update(User, session=session)
                    .where(User.id == user.id)
                    .values(points=user.points + 1)
                    .execute()
                )

        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

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
    },
)
async def first_unverified_handler(
    user: Annotated[User, Depends(get_current_user)],
) -> LinkToVerifyModel | Response:
    """
    Get the first unverified link with max priority from the database and return it.
    Patch the links.user_id field by user's ID who took it.
    If the user already took a link and did not check it return this link again.
    """
    async with CRUD() as session:
        try:
            already_taken_link_result: Result = (
                await CRUD.get(Link, session=session)
                .where(Link.user_id == user.id, Link.is_prohibited.is_(None))
                .limit(1)
                .execute()
            )
            already_taken_link: Link | None = (
                already_taken_link_result.scalar_one_or_none()
            )
            if already_taken_link:
                return LinkToVerifyModel(link=already_taken_link.link)

            link_query_result: Result = (
                await CRUD.get(Link, session=session)
                .where(Link.is_prohibited.is_(None), Link.user_id.is_(None))
                .order_by(Link.priority.desc())
                .limit(1)
                .with_for_update()
                .execute()
            )
            first_unverified_link: Link | None = link_query_result.scalar_one_or_none()
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        if not first_unverified_link:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        try:
            await (
                CRUD.update(Link, session=session)
                .where(Link.id == first_unverified_link.id)
                .values(user_id=user.id)
                .execute()
            )
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

    return LinkToVerifyModel(link=first_unverified_link.link)
