from typing import Annotated

from pydantic import BaseModel, Field


class NewPurchaseModel(BaseModel):
    item_name: Annotated[
        str, Field(default=..., title="Item name", examples=["Milk", "Amogus"])
    ]
    item_amount: Annotated[
        int, Field(default=..., title="Item amount", examples=[1, 10])
    ]
