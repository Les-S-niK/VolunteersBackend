import pytest
from conftest import (
    api_patch,
    assert_error_detail,
    assert_no_content,
    assert_validation_error,
)
from sqlalchemy import Result
from uuid import uuid4

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Link


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_link_status_success(
    session, auth_headers, current_user_id, create_link
):
    link = await create_link(
        link=f"https://after-verification-success-{uuid4().hex}.example.com/",
        user_id=current_user_id,
    )

    try:
        response = api_patch(
            session,
            "/api/v1/links/after_verification/",
            json={"link": link.link, "is_prohibited": True, "violation_type": "Danger"},
            headers=auth_headers,
        )

        assert_no_content(response, 204)

        link_query_result: Result = (
            await CRUD.get(Link).where(Link.id == link.id).execute()
        )
        updated_link: Link | None = link_query_result.scalar_one_or_none()

        assert updated_link is not None
        assert updated_link.is_prohibited is True
    finally:
        await CRUD.delete(Link).where(Link.id == link.id).execute()


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_link_status_forbidden_not_owner(
    session, auth_headers, another_user, create_link
):
    if another_user is None:
        pytest.skip("No second user available in database")

    link = await create_link(
        link=f"https://after-verification-forbidden-{uuid4().hex}.example.com/",
        user_id=another_user.id,
    )

    try:
        response = api_patch(
            session,
            "/api/v1/links/after_verification/",
            json={
                "link": link.link,
                "is_prohibited": False,
                "violation_type": "Amogus",
            },
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert_error_detail(response, "You can not access this link.")
    finally:
        await CRUD.delete(Link).where(Link.id == link.id).execute()


def test_patch_link_not_found(session, auth_headers):
    response = api_patch(
        session,
        "/api/v1/links/after_verification/",
        json={
            "link": f"https://nonexistent-domain-{uuid4().hex}.com",
            "is_prohibited": True,
            "violation_type": "Amogus",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert_error_detail(response, "Link not found or checked already.")


def test_patch_link_validation_error_invalid_url(session, auth_headers):
    response = api_patch(
        session,
        "/api/v1/links/after_verification/",
        json={
            "link": "not-a-valid-url",
            "is_prohibited": True,
            "violation_type": "Amogus",
        },
        headers=auth_headers,
    )

    assert_validation_error(response)


def test_patch_link_validation_error_missing_field(session, auth_headers):
    response = api_patch(
        session,
        "/api/v1/links/after_verification/",
        json={"link": "https://example.com"},
        headers=auth_headers,
    )

    assert_validation_error(response)


def test_patch_link_unauthorized_no_token(session):
    response = api_patch(
        session,
        "/api/v1/links/after_verification/",
        json={
            "link": "https://example.com",
            "is_prohibited": True,
            "violation_type": "Amogus",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_link_false_value(
    session, auth_headers, current_user_id, create_link
):
    link = await create_link(
        link=f"https://after-verification-false-{uuid4().hex}.example.com/",
        user_id=current_user_id,
    )

    try:
        response = api_patch(
            session,
            "/api/v1/links/after_verification/",
            json={
                "link": link.link,
                "is_prohibited": False,
                "violation_type": "Amogus",
            },
            headers=auth_headers,
        )

        assert_no_content(response, 204)

        link_query_result: Result = (
            await CRUD.get(Link).where(Link.id == link.id).execute()
        )
        updated_link: Link | None = link_query_result.scalar_one_or_none()

        assert updated_link is not None
        assert updated_link.is_prohibited is False
    finally:
        await CRUD.delete(Link).where(Link.id == link.id).execute()
