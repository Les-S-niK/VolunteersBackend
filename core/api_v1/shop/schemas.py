from typing import Annotated
from decimal import Decimal

from pydantic import BaseModel, Field


class NewPurchaseModel(BaseModel):
    item_name: Annotated[
        str, Field(default=..., title="Item name", examples=["Milk", "Amogus"])
    ]
    item_amount: Annotated[
        int, Field(default=..., title="Item amount", ge=1, examples=[1, 10])
    ]


class ItemModel(BaseModel):
    id: int
    image_url: Annotated[str, Field(default=..., title="Image URL")]
    price: Annotated[
        Decimal, Field(default=..., title="Item price", examples=[1000, 80.2], ge=0)
    ]
    amount: Annotated[
        int, Field(default=..., title="Item amount", examples=[1, 10], ge=0)
    ]
    name: Annotated[
        str, Field(default=..., title="Item name", examples=["Milk", "Amogus"])
    ]
