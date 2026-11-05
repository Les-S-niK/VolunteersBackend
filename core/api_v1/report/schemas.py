from typing import Annotated
from pydantic import BaseModel, Field


class ReportModel(BaseModel):
    title: Annotated[
        str,
        Field(
            default=...,
            title="Report Title",
            min_length=12,
            max_length=200,
            examples=["Important Report", "Api does not work!"],
        ),
    ]
    description: Annotated[
        str,
        Field(
            default=...,
            title="Report Description",
            min_length=12,
            max_length=5000,
            examples=["Very informative description.", "Example"],
        ),
    ]
