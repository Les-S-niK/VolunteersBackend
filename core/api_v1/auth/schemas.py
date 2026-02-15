from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber


PHONE_NUMBER_KEY: str = "phone_number"


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
            examples=["Bearer"],
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
            examples=[{"phone_number": "+79998882020", "exp": "2026-02-15 20:47"}],
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


class RussianPhoneNumber(PhoneNumber):
    ## Starts with Russian region code (+7)
    default_region_code = "RU"


class UserAuth(BaseModel):
    phone_number: Annotated[
        RussianPhoneNumber,
        Field(
            default=...,
            alias="phone_number",
            title="Phone Number",
            description="User's phone number representation.",
            examples=["+79998881020"],
        ),
    ]
    password: Annotated[
        SecretStr,
        Field(
            default=...,
            alias="password",
            title="Password",
            description="User's password",
            examples=["VeryStrongPassword1234"],
        ),
    ]
