from typing import Annotated
from pydantic import BaseModel, Field


class ReportModel(BaseModel):
    title: Annotated[
        str,
        Field(
            default=...,
            title="Report Title",
            examples=["Important Report", "Api does not work!"],
        ),
    ]
    description: Annotated[
        str,
        Field(
            default=...,
            title="Report Description",
            examples=["Very informative description.", "Example"],
        ),
    ]
