from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from core.api_v1.auth.utils import get_current_user
from core.api_v1.error_schemas import (
    InternalServerError,
    NotFoundError,
    UnprocessableContentError,
)
from core.api_v1.http_exceptions import internal_server_error
from core.api_v1.shop.schemas import ItemModel, NewPurchaseModel
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Item, PurchaseStatuses, User, UserItem

shop_router: APIRouter = APIRouter(prefix="/api/v1/shop", tags=["Shop"])


@shop_router.post(
    path="/new_purchase/",
    responses={
        status.HTTP_201_CREATED: {"description": "Purchase added in the database."},
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundError,
            "description": "Item not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": UnprocessableContentError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
    status_code=status.HTTP_201_CREATED,
)
async def new_purchase_handler(
    user: Annotated[User, Depends(get_current_user)],
    new_purchase_model: Annotated[NewPurchaseModel, Body()],
) -> Response:
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
        try:
            user_result: Result = await (
                CRUD.get(User, session=session)
                .where(User.id == user.id)
                .with_for_update()
                .execute()
            )
            new_user: User | None = user_result.scalar_one_or_none()
            if not new_user:
                await session.rollback()
                raise internal_server_error

            if new_user.points < item.price * new_purchase_model.item_amount:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="The user can not buy the item if he does not have enough points.",
                )

            user_item: UserItem = UserItem(
                user_id=user.id, item_id=item.id, status=PurchaseStatuses.frozen
            )
            await CRUD.add(user_item, session=session).execute()
            await (
                CRUD.update(Item, session=session)
                .where(Item.id == item.id)
                .values(amount=item.amount - new_purchase_model.item_amount)
                .execute()
            )
            await (
                CRUD.update(User, session=session)
                .where(User.id == new_user.id)
                .values(
                    points=new_user.points - item.price * new_purchase_model.item_amount
                )
                .execute()
            )
        except SQLAlchemyError:
            await session.rollback()
            raise internal_server_error

        return Response(status_code=status.HTTP_201_CREATED)


@shop_router.get(
    path="/all_items/",
    responses={
        status.HTTP_200_OK: {
            "model": list[ItemModel],
            "description": "All the items in the database.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def all_items_handler(
    _: Annotated[User, Depends(get_current_user)],
) -> list[ItemModel]:
    try:
        result: Result = await CRUD.get(Item).where().execute()
    except SQLAlchemyError:
        raise internal_server_error
    database_items: list[ItemModel] = list(result.scalars().all())

    return database_items
