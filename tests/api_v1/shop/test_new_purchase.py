from decimal import Decimal
from uuid import uuid4

import pytest
from conftest import (
    TEST_USER_POINTS,
    api_post,
    assert_error_detail,
    assert_no_content,
    assert_validation_error,
)
from sqlalchemy import Result

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Item, PurchaseStatuses, User, UserItem


def test_post_new_purchase_unauthorized(session):
    response = api_post(
        session,
        "/api/v1/shop/new_purchase/",
        json={"item_name": "Milk", "item_amount": 1},
    )

    assert response.status_code == 401


def test_post_new_purchase_validation_error_missing_item_name(session, auth_headers):
    response = api_post(
        session,
        "/api/v1/shop/new_purchase/",
        json={"item_amount": 1},
        headers=auth_headers,
    )

    assert_validation_error(response)


def test_post_new_purchase_validation_error_invalid_item_amount(
    session, auth_headers
):
    response = api_post(
        session,
        "/api/v1/shop/new_purchase/",
        json={"item_name": "Milk", "item_amount": 0},
        headers=auth_headers,
    )

    assert_validation_error(response)


def test_post_new_purchase_not_found(session, auth_headers):
    response = api_post(
        session,
        "/api/v1/shop/new_purchase/",
        json={"item_name": f"missing-item-{uuid4().hex}", "item_amount": 1},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert_error_detail(response, "Item not found")


@pytest.mark.asyncio(loop_scope="session")
async def test_post_new_purchase_unprocessable_when_not_enough_items(
    session, auth_headers, create_item
):
    item = await create_item(price=Decimal("1"), amount=1)

    try:
        response = api_post(
            session,
            "/api/v1/shop/new_purchase/",
            json={"item_name": item.name, "item_amount": 2},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert_error_detail(
            response,
            "The user can not buy more items than there are in stock.",
        )
    finally:
        await CRUD.delete(Item).where(Item.id == item.id).execute()


@pytest.mark.asyncio(loop_scope="session")
async def test_post_new_purchase_unprocessable_when_not_enough_points(
    session, auth_headers, current_user_id, create_item
):
    item = await create_item(price=Decimal("100"), amount=5)
    await CRUD.update(User).where(User.id == current_user_id).values(points=10).execute()

    try:
        response = api_post(
            session,
            "/api/v1/shop/new_purchase/",
            json={"item_name": item.name, "item_amount": 1},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert_error_detail(
            response,
            "The user can not buy the item if he does not have enough points.",
        )
    finally:
        await CRUD.update(User).where(User.id == current_user_id).values(points=TEST_USER_POINTS).execute()
        await CRUD.delete(Item).where(Item.id == item.id).execute()


@pytest.mark.asyncio(loop_scope="session")
async def test_post_new_purchase_success_creates_purchase_and_updates_balances(
    session, auth_headers, current_user_id, create_item
):
    item = await create_item(price=Decimal("7"), amount=3)
    await CRUD.update(User).where(User.id == current_user_id).values(points=100).execute()

    try:
        response = api_post(
            session,
            "/api/v1/shop/new_purchase/",
            json={"item_name": item.name, "item_amount": 2},
            headers=auth_headers,
        )

        assert_no_content(response, 201)

        user_item_query_result: Result = (
            await CRUD.get(UserItem)
            .where(UserItem.user_id == current_user_id)
            .where(UserItem.item_id == item.id)
            .execute()
        )
        user_item: UserItem | None = user_item_query_result.scalar_one_or_none()

        item_query_result: Result = (
            await CRUD.get(Item)
            .where(Item.id == item.id)
            .execute()
        )
        updated_item: Item | None = item_query_result.scalar_one_or_none()

        updated_user_query_result: Result = (
            await CRUD.get(User)
            .where(User.id == current_user_id)
            .execute()
        )
        updated_user: User | None = updated_user_query_result.scalar_one_or_none()

        assert user_item is not None
        assert user_item.status == PurchaseStatuses.frozen
        assert updated_item is not None
        assert updated_item.amount == 1
        assert updated_user is not None
        assert updated_user.points == 86
    finally:
        await CRUD.update(User).where(User.id == current_user_id).values(points=TEST_USER_POINTS).execute()
        await CRUD.delete(UserItem).where(UserItem.item_id == item.id).execute()
        await CRUD.delete(Item).where(Item.id == item.id).execute()
