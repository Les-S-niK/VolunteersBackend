from typing import Annotated
from pydantic import BaseModel, Field


class ApplicantModel(BaseModel):
    name: Annotated[
        str,
        Field(
            default=...,
            title="Applicant name",
            min_length=1,
            max_length=200,
            examples=["GoodName"],
        ),
    ]
    region: Annotated[
        str,
        Field(
            default=...,
            title="Applicant region",
            min_length=1,
            max_length=200,
            examples=["Sochi"],
        ),
    ]
    contact: Annotated[
        str,
        Field(
            default=...,
            title="Applicant contact",
            min_length=1,
            max_length=200,
            examples=["+7 999 111 81 81", "@applicantProfile"],
        ),
    ]
    content: Annotated[
        str | None,
        Field(
            default=...,
            title="Application request content",
            max_length=5000,
            examples=["Information about this request."],
        ),
    ]
