from conftest import BASE_URL, assert_schema


USER_EVENTS_SCHEMA = {
    "events": list
}


def test_get_user_events_success(session, auth_headers):
    response = session.get(
        f"{BASE_URL}/api/v1/profiles/user_events/",
        headers=auth_headers
    )
    assert response.status_code == 200

    body = response.json()
    assert_schema(body, USER_EVENTS_SCHEMA)


def test_get_user_events_unauthorized(session):
    response = session.get(f"{BASE_URL}/api/v1/profiles/user_events/")
    assert response.status_code == 401