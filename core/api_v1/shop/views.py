from typing import Annotated
from fastapi import APIRouter, Body, Depends, status

from core.api_v1.auth.utils import get_current_user
from core.database.sqlalchemy.models import User
from core.api_v1.shop.schemas import NewPurchaseModel


shop_router: APIRouter = APIRouter(prefix="/api/v1/shop", tags=["Shop"])


@shop_router.post(
    path="/new_purchase/", responses={}, status_code=status.HTTP_201_CREATED
)
async def new_purchase_handler(
    user: Annotated[User, Depends(get_current_user)],
    new_purchase_model: Annotated[NewPurchaseModel, Body()],
) -> None: ...
