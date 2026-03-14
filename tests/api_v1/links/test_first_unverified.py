import pytest
from conftest import BASE_URL
from sqlalchemy import Result
from uuid import uuid4

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Link


def test_patch_first_unverified_success(session, auth_headers):
    response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=auth_headers,
    )

    assert response.status_code in (200, 204)
    if response.status_code == 200:
        body = response.json()
        assert "link" in body
        assert isinstance(body["link"], str)


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_first_unverified_sets_current_user_id(
    session, auth_headers, valid_credentials
):
    response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=auth_headers,
    )

    if response.status_code == 204:
        return

    assert response.status_code == 200
    link_url = response.json()["link"]
    link_query_result: Result = (
        await CRUD.get(Link).where(Link.link == link_url).execute()
    )
    link: Link | None = link_query_result.scalar_one_or_none()

    assert link is not None
    assert link.user_id == int(valid_credentials["user_id"])


def test_patch_first_unverified_unauthorized_no_token(session):
    response = session.patch(f"{BASE_URL}/api/v1/links/first_unverified/")
    assert response.status_code == 401


def test_patch_first_unverified_unauthorized_invalid_token(session):
    headers = {"Authorization": "Bearer invalid-token"}
    response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_first_unverified_returns_highest_priority_link(
    session, auth_headers, valid_credentials
):
    low_priority_url = f"https://first-unverified-low-{uuid4().hex}.example.com"
    high_priority_url = f"https://first-unverified-high-{uuid4().hex}.example.com"

    low_link = Link(
        link=low_priority_url, is_prohibited=None, priority=10_000, user_id=None
    )
    high_link = Link(
        link=high_priority_url, is_prohibited=None, priority=10_001, user_id=None
    )

    await CRUD.add(low_link).execute()
    await CRUD.add(high_link).execute()

    try:
        response = session.patch(
            f"{BASE_URL}/api/v1/links/first_unverified/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["link"].rstrip("/") == high_priority_url.rstrip("/")

        high_link_query: Result = (
            await CRUD.get(Link).where(Link.link == high_priority_url).execute()
        )
        found_high_link: Link | None = high_link_query.scalar_one_or_none()

        assert found_high_link is not None
        assert found_high_link.user_id == int(valid_credentials["user_id"])
    finally:
        await (
            CRUD.delete(Link)
            .where(Link.link.in_([low_priority_url, high_priority_url]))
            .execute()
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_first_unverified_returns_no_content_when_no_unverified_links(
    session, auth_headers
):
    unverified_links_query: Result = (
        await CRUD.get(Link).where(Link.is_prohibited.is_(None)).execute()
    )
    unverified_links = list(unverified_links_query.scalars().all())
    unverified_ids = [link.id for link in unverified_links]

    try:
        if unverified_ids:
            await (
                CRUD.update(Link)
                .where(Link.id.in_(unverified_ids))
                .values(is_prohibited=False)
                .execute()
            )

        response = session.patch(
            f"{BASE_URL}/api/v1/links/first_unverified/",
            headers=auth_headers,
        )

        assert response.status_code == 204
        assert response.text == ""
    finally:
        if unverified_ids:
            await (
                CRUD.update(Link)
                .where(Link.id.in_(unverified_ids))
                .values(is_prohibited=None)
                .execute()
            )

