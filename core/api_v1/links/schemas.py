from typing import Annotated

from pydantic import BaseModel, Field


class LinkToVerifyModel(BaseModel):
    link: Annotated[
        str,
        Field(
            default=...,
            title="Site URL",
            description="URL that need to be checked for prohibition.",
            examples=["https://example.com/"],
        ),
    ]


class VerifiedLinkResult(LinkToVerifyModel):
    is_prohibited: Annotated[
        bool,
        Field(
            default=...,
            description="Is link prohibited? True - yes, False - no.",
            examples=[False],
        ),
    ]
    violation_type: Annotated[
        str | None,
        Field(
            default=None,
            description="Link violation type.",
            examples=["Type1", "Danger"],
        ),
    ]
    content_type: Annotated[
        list[str] | None,
        Field(
            default=None, description="Link content types", examples=[["Text", "Image"]]
        ),
    ]
