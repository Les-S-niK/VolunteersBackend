import pytest
from conftest import api_patch, assert_no_content
from sqlalchemy import Result
from uuid import uuid4

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Link


def test_patch_first_unverified_success(session, auth_headers):
    response = api_patch(session, "/api/v1/links/first_unverified/", headers=auth_headers)

    assert response.status_code in (200, 204)
    if response.status_code == 200:
        body = response.json()
        assert "link" in body
        assert isinstance(body["link"], str)


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_first_unverified_sets_current_user_id(
    session, auth_headers, current_user_id
):
    async with CRUD() as cleanup_session:
        await (
            CRUD.delete(Link, session=cleanup_session)
            .where(Link.user_id == current_user_id, Link.is_prohibited.is_(None))
            .execute()
        )

    test_link_url = f"https://first-unverified-test-{uuid4().hex}.example.com"
    test_link = Link(
        link=test_link_url,
        is_prohibited=None,
        priority=10**9,
        user_id=None,
    )
    await CRUD.add(test_link).execute()

    try:
        response = api_patch(session, "/api/v1/links/first_unverified/", headers=auth_headers)

        assert response.status_code == 200
        link_url = response.json()["link"]
        assert link_url.rstrip("/") == test_link_url.rstrip("/")

        link_query_result: Result = (
            await CRUD.get(Link).where(Link.link == test_link_url).execute()
        )
        link: Link | None = link_query_result.scalar_one_or_none()
        assert link is not None
        assert link.user_id == current_user_id
    finally:
        await CRUD.delete(Link).where(Link.id == test_link.id).execute()


def test_patch_first_unverified_unauthorized_no_token(session):
    response = api_patch(session, "/api/v1/links/first_unverified/")
    assert response.status_code == 401


def test_patch_first_unverified_unauthorized_invalid_token(session):
    headers = {"Authorization": "Bearer invalid-token"}
    response = api_patch(session, "/api/v1/links/first_unverified/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_first_unverified_returns_highest_priority_link(
    session, auth_headers, current_user_id
):
    async with CRUD() as cleanup_session:
        await (
            CRUD.delete(Link, session=cleanup_session)
            .where(Link.user_id == current_user_id, Link.is_prohibited.is_(None))
            .execute()
        )

    low_priority_url = f"https://first-unverified-low-{uuid4().hex}.example.com"
    high_priority_url = f"https://first-unverified-high-{uuid4().hex}.example.com"

    low_link = Link(
        link=low_priority_url, is_prohibited=None, priority=10**9, user_id=None
    )
    high_link = Link(
        link=high_priority_url, is_prohibited=None, priority=10**9 + 1, user_id=None
    )

    await CRUD.add(low_link).execute()
    await CRUD.add(high_link).execute()

    try:
        response = api_patch(session, "/api/v1/links/first_unverified/", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["link"].rstrip("/") == high_priority_url.rstrip("/")

        high_link_query: Result = (
            await CRUD.get(Link).where(Link.link == high_priority_url).execute()
        )
        found_high_link: Link | None = high_link_query.scalar_one_or_none()

        assert found_high_link is not None
        assert found_high_link.user_id == current_user_id
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
    existing_unverified_links_query: Result = (
        await CRUD.get(Link).where(Link.is_prohibited.is_(None)).execute()
    )
    existing_unverified_links = list(existing_unverified_links_query.scalars().all())

    if existing_unverified_links:
        pytest.skip(
            "Database already contains unverified links; "
            "the endpoint is global, so asserting 204 without mutating shared state would be unsafe."
        )

    verified_link = Link(
        link=f"https://first-unverified-none-{uuid4().hex}.example.com",
        is_prohibited=False,
        priority=1,
        user_id=None,
    )
    await CRUD.add(verified_link).execute()

    try:
        response = api_patch(session, "/api/v1/links/first_unverified/", headers=auth_headers)
        assert_no_content(response, 204)
    finally:
        await CRUD.delete(Link).where(Link.id == verified_link.id).execute()
