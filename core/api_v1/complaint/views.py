from typing import Annotated

from fastapi import APIRouter, Body, Response, status
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.complaint import ComplaintModel
from core.api_v1.error_schemas import InternalServerError, TooManyRequestsError
from core.api_v1.http_exceptions import internal_server_error
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Complaint

complaints_router: APIRouter = APIRouter(
    prefix="/api/v1/complaints",
    tags=["Complaints"],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": TooManyRequestsError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)


@complaints_router.post(
    path="/new_complaint/",
    description="Create a new complaint by unauthorized user.",
    responses={
        status.HTTP_201_CREATED: {"description": "Complaint successfully added."},
    },
)
async def new_complaint_handler(
    complaint: Annotated[ComplaintModel, Body()],
) -> Response:
    complaint_db_model: Complaint = Complaint(
        type=complaint.type,
        sender=complaint.sender,
        sender_contact=complaint.sender_contact,
        content=complaint.content,
    )
    try:
        await CRUD.add(complaint_db_model).execute()
    except SQLAlchemyError:
        raise internal_server_error

    return Response(status_code=status.HTTP_201_CREATED)
