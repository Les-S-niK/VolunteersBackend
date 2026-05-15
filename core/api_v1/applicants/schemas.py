from typing import Annotated
from pydantic import BaseModel, Field


class ApplicantModel(BaseModel):
    name: Annotated[
        str, Field(default=..., title="Applicant name", examples=["GoodName"])
    ]
    region: Annotated[
        str, Field(default=..., title="Applicant region", examples=["Sochi"])
    ]
    contact: Annotated[
        str,
        Field(
            default=...,
            title="Applicant contact",
            examples=["+7 999 111 81 81", "@applicantProfile"],
        ),
    ]
    content: Annotated[
        str | None,
        Field(
            default=...,
            title="Application request content",
            examples=["Information about this request."],
        ),
    ]
