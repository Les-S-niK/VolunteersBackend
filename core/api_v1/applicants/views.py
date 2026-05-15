from typing import Annotated

from fastapi import APIRouter, Body, Response, status
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.applicants.schemas import ApplicantModel
from core.api_v1.error_schemas import InternalServerError, TooManyRequestsError
from core.api_v1.http_exceptions import internal_server_error
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Applicant

applicants_router: APIRouter = APIRouter(
    prefix="/api/v1/applicants",
    tags=["Applicants"],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": TooManyRequestsError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)


@applicants_router.post(
    path="/new_applicant/",
    description="Add a new applicant request in the database.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Applicant request successfully added into the database."
        }
    },
)
async def new_applicant_handler(
    applicant: Annotated[ApplicantModel, Body()],
) -> Response:
    applicant_db_model: Applicant = Applicant()
    applicant_db_model.name = applicant.name
    applicant_db_model.contact = applicant.contact
    applicant_db_model.region = applicant.region
    applicant_db_model.content = applicant.content

    try:
        await CRUD.add(applicant_db_model).execute()
    except SQLAlchemyError:
        raise internal_server_error

    return Response(status_code=status.HTTP_201_CREATED)
