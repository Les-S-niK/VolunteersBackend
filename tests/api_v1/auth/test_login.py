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
        json={"user_id": valid_credentials["user_id"], "password": "wrong", "city_id": valid_credentials["city_id"]}
    )

    assert response.status_code != 500
    assert response.status_code == 401


def test_login_invalid_city_id(session, valid_credentials):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json={"user_id": valid_credentials["user_id"], "password": valid_credentials["password"], "city_id": -1}
    )

    assert response.status_code != 500
    assert response.status_code == 401


def test_login_invalid_user(session, valid_credentials):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json={"user_id": "-1", "password": valid_credentials["password"], "city_id": valid_credentials["city_id"]}
    )

    assert response.status_code != 500
    assert response.status_code == 401


@pytest.mark.parametrize("payload", [
    {},
    {"user_id": ""},
    {"password": ""},
    {"city_id": ""},
    {"user_id": 123, "password": True, "city_id": 1000},
    {"user_id": None, "password": None, "city_id": None},
    {"user_id": "a"*1000, "password": "b"*1000, "city_id": 2**100},
])
def test_login_bad_input(session, payload):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=payload
    )

    assert response.status_code != 500
    assert response.status_code in (401, 422)