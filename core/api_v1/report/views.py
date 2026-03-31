from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response, status
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_201_CREATED

from core.api_v1.auth import get_current_user
from core.api_v1.error_schemas import (
    InternalServerError,
    NotAuthorized,
    TooManyRequestsError,
)
from core.api_v1.http_exceptions import internal_server_error
from core.api_v1.report.schemas import ReportModel
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Report, ReportStatuses, User

reports_router: APIRouter = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": NotAuthorized},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": TooManyRequestsError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)


@reports_router.post(
    path="/new/",
    description="Add a new report in the database.",
    responses={
        status.HTTP_201_CREATED: {"description": "Report added in the database."},
    },
    status_code=status.HTTP_201_CREATED,
)
async def new_report_handler(
    user: Annotated[User, Depends(get_current_user)],
    report_model: Annotated[ReportModel, Body()],
) -> Response:
    """
    Add a new report in the database.
    Write a new report based on report_model provided by user.

    Returns:
        Response: status 201 with no body.
    """
    report: Report = Report(
        title=report_model.title,
        description=report_model.description,
        status=ReportStatuses.unanswered,
        user_id=user.id,
    )
    try:
        await CRUD.add(report).execute()
    except SQLAlchemyError:
        raise internal_server_error

    return Response(status_code=HTTP_201_CREATED)
