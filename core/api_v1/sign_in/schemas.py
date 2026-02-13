from typing import Annotated

from pydantic import BaseModel, Field, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class RussianPhoneNumber(PhoneNumber):
    ## Starts with Russian region code (+7)
    default_region_code = "RU"


class UserSignIn(BaseModel):
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
