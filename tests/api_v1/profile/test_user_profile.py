import pytest
from conftest import TEST_USER_POINTS, api_get, assert_schema


USER_PROFILE_SCHEMA = {
    "id": int,
    "city_id": int,
    "points": int
}


def test_get_user_profile_success(session, auth_headers):
    response = api_get(session, "/api/v1/profiles/user_profile/", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert_schema(body, USER_PROFILE_SCHEMA)


def test_get_user_profile_unauthorized(session):
    response = api_get(session, "/api/v1/profiles/user_profile/")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_profile_returns_current_user_data(
    session, auth_headers, valid_credentials
):
    response = api_get(session, "/api/v1/profiles/user_profile/", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == int(valid_credentials["user_id"])
    assert body["city_id"] == int(valid_credentials["city_id"])
    assert body["points"] == TEST_USER_POINTS
