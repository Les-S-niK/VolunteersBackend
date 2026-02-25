from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field, SecretStr


USER_ID_KEY: str = "user_id"


class TokenTypesEnum(StrEnum):
    access = "access"
    refresh = "refresh"


class EncodedTokensPair(BaseModel):
    access_token: Annotated[
        str,
        Field(
            default=...,
            alias="access_token",
            title="Encoded access token",
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZV9udW1iZXIiOiJ0ZWw6KzctOTk5LTg4OC0xMC0yMCIsImV4cCI6MTc3MTQyOTI5M30.t-Bu64pxxOyrDvs15fcN0fjcsSF_RErY2V3JbkCL0Sk"
            ],
        ),
    ]
    refresh_token: Annotated[
        str,
        Field(
            default=...,
            alias="refresh_token",
            title="Encoded refresh token",
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZV9udW1iZXIiOiJ0ZWw6KzctOTk5LTg4OC0xMC0yMCIsImV4cCI6MTc3MTQyOTI5M30.t-Bu64pxxOyrDvs15fcN0fjcsSF_RErY2V3JbkCL0Sk"
            ],
        ),
    ]


class EncodedToken(BaseModel):
    token: Annotated[
        str,
        Field(
            default=...,
            alias="token",
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
            examples=["access", "refresh"],
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
            examples=[{USER_ID_KEY: 123, "exp": "2026-02-15 20:47"}],
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


class UserAuth(BaseModel):
    user_id: Annotated[
        int,
        Field(
            default=...,
            alias="user_id",
            title="User ID",
            description="User's id in the database.",
            examples=[123, 199, 1],
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
