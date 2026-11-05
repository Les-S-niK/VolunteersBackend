from typing import Annotated

from pydantic import BaseModel, Field  # noqa: F401


class ComplaintModel(BaseModel):
    ## Complaint does not refer to a specific user because it can be anonymous. ##
    ## User may not login in the API to send complaints. ##

    ## I should change complaint type to Enum but no one knows all the complaint types that will be in the application. Yep. ##
    type: Annotated[
        str,
        Field(
            default=...,
            title="Type",
            min_length=1,
            max_length=80,
            examples=["Person", "Group"],
        ),
    ]
    sender: Annotated[
        str | None,
        Field(
            default=None,
            title="Sender",
            max_length=200,
            examples=["SenderName"],
        ),
    ]
    sender_contact: Annotated[
        str | None,
        Field(
            default=None,
            title="Sender contact",
            description="Sender contact information for feedback.",
            max_length=200,
            examples=["@myTelegramProfile"],
        ),
    ]
    content: Annotated[
        str,
        Field(
            default=...,
            title="Content",
            max_length=2000,
            examples=["Important complaint"],
        ),
    ]
