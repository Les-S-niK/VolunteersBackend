from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field

from config import TOKEN_TYPE

## Phone number field in encoded token.
PHONE_NUMBER_FIELD: str = "phone_number"


class EncodedToken(BaseModel):
    encoded_payload: Annotated[
        str,
        Field(
            default=...,
            alias="encoded_payload",
            title="Encoded Token Payload",
            description="Encoded token payload with user data.",
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZV9udW1iZXIiOiJ0ZWw6KzctOTk5LTg4OC0xMC0yMCIsImV4cCI6MTc3MTQyOTI5M30.t-Bu64pxxOyrDvs15fcN0fjcsSF_RErY2V3JbkCL0Sk"
            ],
        ),
    ]
    token_type: Annotated[
        str,
        Field(
            default=...,
            alias="token_type",
            title="Token Type",
            description="JWT token type.",
            examples=[TOKEN_TYPE],
        ),
    ]


class DecodedToken(BaseModel):
    decoded_payload: Annotated[
        dict[str, Any],
        Field(
            default=...,
            alias="decoded_payload",
            title="Decoded Token Payload",
            description="Decoded token payload with user data.",
            examples=[{"phone_number": "+79998882020"}],
        ),
    ]
    expiration_date: Annotated[
        datetime,
        Field(
            default=...,
            alias="expiration_date",
            title="Expiration Date",
            description="Decoded token expiration date.",
            examples=["2026-02-13 18:52"],
        ),
    ]
