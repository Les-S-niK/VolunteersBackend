from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl


class LinkToVerifyModel(BaseModel):
    link: Annotated[
        HttpUrl,
        Field(
            default=...,
            title="Site URL",
            description="URL that need to be checked for prohibition.",
            examples=["https://example.com"],
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
