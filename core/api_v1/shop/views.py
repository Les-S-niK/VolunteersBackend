from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.auth.utils import get_current_user
from core.api_v1.http_exceptions import internal_server_error
from core.api_v1.shop.schemas import NewPurchaseModel
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Item, PurchaseStatuses, User, UserItem

shop_router: APIRouter = APIRouter(prefix="/api/v1/shop", tags=["Shop"])


@shop_router.post(
    path="/new_purchase/", responses={}, status_code=status.HTTP_201_CREATED
)
async def new_purchase_handler(
    user: Annotated[User, Depends(get_current_user)],
    new_purchase_model: Annotated[NewPurchaseModel, Body()],
) -> None:
    async with CRUD() as session:
        try:
            item_result: Result = (
                await CRUD.get(Item, session=session)
                .where(Item.name == new_purchase_model.item_name)
                .with_for_update()
                .execute()
            )
            item: Item | None = item_result.scalar_one_or_none()
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        if not item:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
        if new_purchase_model.item_amount > item.amount:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="The user can not buy more items than there are in stock.",
            )
        if user.points < item.price:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="The user can not buy the item if he does not have enough points.",
            )

        user_item: UserItem = UserItem(
            user_id=user.id, item_id=item.id, status=PurchaseStatuses.frozen
        )
        try:
            await CRUD.add(user_item, session=session).execute()
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        try:
            user_result: Result = await (
                CRUD.get(User, session=session)
                .where(User.id == user.id)
                .with_for_update()
                .execute()
            )
            new_user: User | None = user_result.scalar_one_or_none()
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        if not new_user:
            await session.rollback()
            raise internal_server_error

        try:
            await (
                CRUD.update(User, session=session)
                .where(User.id == new_user.id)
                .values(points=new_user.points - item.price)
                .execute()
            )
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        await session.commit()
