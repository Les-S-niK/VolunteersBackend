from conftest import BASE_URL, assert_schema


USER_PROFILE_SCHEMA = {
    "id": int,
    "full_name": str,
    "points": int
}


def test_get_user_profile_success(session, auth_headers):
    headers = auth_headers
    response = session.get(
        f"{BASE_URL}/api/v1/profiles/user_profile/",
        headers=headers
    )
    assert response.status_code == 200

    body = response.json()
    
    assert_schema(body, USER_PROFILE_SCHEMA)


def test_get_user_profile_unauthorized(session):
    response = session.get(f"{BASE_URL}/api/v1/profiles/user_profile/")
    assert response.status_code == 401