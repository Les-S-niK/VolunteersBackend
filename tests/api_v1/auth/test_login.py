from conftest import BASE_URL, TEST_DELAY, assert_schema
from time import sleep
import pytest



AUTH_LOGIN_SCHEMA = {
    "token": str,
    "token_type": str
}


def test_login_success(session, valid_credentials):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert response.status_code == 200
    
    body = response.json()
    
    assert_schema(body, AUTH_LOGIN_SCHEMA)
    assert "refresh_token" in session.cookies


def test_login_returns_unique_tokens(session, valid_credentials):
    r1 = session.post(
        f"{BASE_URL}/api/v1/auth/login/", 
        json=valid_credentials
    )
    token1 = r1.json()["token"]
    refresh1 = session.cookies.get("refresh_token")
    session.cookies.clear()
    sleep(TEST_DELAY)
    r2 = session.post(f"{BASE_URL}/api/v1/auth/login/", json=valid_credentials)
    token2 = r2.json()["token"]
    refresh2 = session.cookies.get("refresh_token")
    
    assert token1 != token2
    assert refresh1 != refresh2


def test_login_invalid_password(session, valid_credentials):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json={"user_id": valid_credentials["user_id"], "password": "wrong"}
    )

    assert response.status_code == 422
    assert response.status_code != 500


def test_login_invalid_user(session):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json={"user_id": "0", "password": "wrong"}
    )

    assert response.status_code == 422
    assert response.status_code != 500


@pytest.mark.parametrize("payload", [
    {},
    {"user_id": ""},
    {"password": ""},
    {"user_id": 123, "password": True},
    {"user_id": None, "password": None},
    {"user_id": "a"*1000, "password": "b"*1000},
])
def test_login_bad_input(session, payload):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=payload
    )

    assert response.status_code != 500
    assert response.status_code in (401, 422)

