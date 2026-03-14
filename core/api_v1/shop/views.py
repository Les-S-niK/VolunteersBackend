from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.auth.utils import get_current_user
from core.api_v1.shop.schemas import NewPurchaseModel
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Item, User

shop_router: APIRouter = APIRouter(prefix="/api/v1/shop", tags=["Shop"])


@shop_router.post(
    path="/new_purchase/", responses={}, status_code=status.HTTP_201_CREATED
)
async def new_purchase_handler(
    user: Annotated[User, Depends(get_current_user)],
    new_purchase_model: Annotated[NewPurchaseModel, Body()],
) -> None:
    try:
        item_result: Result = (
            await CRUD.get(Item)
            .where(Item.name == new_purchase_model.item_name)
            .execute()
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    item: Item | None = item_result.scalar_one_or_none()
