import uuid
from decimal import Decimal

import pytest
from conftest import api_get

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Item


def test_all_items_unauthorized(session):
    """Request without authentication should return 401."""
    response = api_get(session, "/api/v1/shop/all_items/")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_all_items_returns_list(session, auth_headers):
    """Authenticated request should return a list (may contain existing items)."""
    response = api_get(
        session,
        "/api/v1/shop/all_items/",
        headers=auth_headers,
    )
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_all_items_contains_created_items(session, auth_headers, create_item):
    """When creating new items, they should appear in the response."""
    unique_name1 = f"item-{uuid.uuid4().hex}"
    unique_name2 = f"item-{uuid.uuid4().hex}"
    item1 = await create_item(name=unique_name1, price=Decimal("10.00"), amount=5)
    item2 = await create_item(name=unique_name2, price=Decimal("20.00"), amount=3)

    try:
        response = api_get(
            session,
            "/api/v1/shop/all_items/",
            headers=auth_headers,
        )
        assert response.status_code == 200
        items = response.json()

        found_items = {item["name"]: item for item in items}
        assert unique_name1 in found_items
        assert unique_name2 in found_items

        assert found_items[unique_name1]["price"] == "10.00"
        assert found_items[unique_name1]["amount"] == 5
        assert found_items[unique_name2]["price"] == "20.00"
        assert found_items[unique_name2]["amount"] == 3

        assert "id" in found_items[unique_name1]
        assert "id" in found_items[unique_name2]

    finally:
        await CRUD.delete(Item).where(Item.id == item1.id).execute()
        await CRUD.delete(Item).where(Item.id == item2.id).execute()
