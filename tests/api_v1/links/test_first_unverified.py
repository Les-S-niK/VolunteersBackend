import asyncio
from conftest import BASE_URL
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


def test_patch_first_unverified_sets_current_user_id(session, auth_headers, valid_credentials):
    response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=auth_headers,
    )

    if response.status_code == 204:
        return

    assert response.status_code == 200
    link_url = response.json()["link"]
    link = asyncio.run(Link.get_by_link(link=link_url))
    assert link is not None
    assert link.user_id == int(valid_credentials["user_id"])


def test_patch_first_unverified_unauthorized_no_token(session):
    response = session.patch(f"{BASE_URL}/api/v1/links/first_unverified/")
    assert response.status_code == 401
