from typing import Annotated

from pydantic import BaseModel, Field


class NewPurchaseModel(BaseModel):
    item_name: Annotated[
        str, Field(default=..., title="Item name", examples=["Milk", "Amogus"])
    ]
    item_amount: Annotated[
        int, Field(default=..., title="Item amount", ge=1, examples=[1, 10])
    ]
