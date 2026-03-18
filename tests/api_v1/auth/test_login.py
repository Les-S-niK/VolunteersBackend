import pytest
from conftest import (
    TEST_DELAY,
    api_post,
    assert_refresh_cookie,
    assert_token_response,
)
from time import sleep


def test_login_success(session, valid_credentials):
    response = api_post(session, "/api/v1/auth/login/", json=valid_credentials)
    assert_token_response(response)
    assert_refresh_cookie(session)


def test_login_returns_unique_tokens(session, valid_credentials):
    response1 = api_post(session, "/api/v1/auth/login/", json=valid_credentials)
    token1 = assert_token_response(response1)["token"]
    refresh1 = assert_refresh_cookie(session)
    session.cookies.clear()
    sleep(TEST_DELAY)

    response2 = api_post(session, "/api/v1/auth/login/", json=valid_credentials)
    token2 = assert_token_response(response2)["token"]
    refresh2 = assert_refresh_cookie(session)

    assert token1 != token2
    assert refresh1 != refresh2


def test_login_invalid_password(session, valid_credentials):
    response = api_post(
        session,
        "/api/v1/auth/login/",
        json={
            "user_id": valid_credentials["user_id"],
            "password": "wrong",
            "city_id": valid_credentials["city_id"],
        },
    )

    assert response.status_code == 401


def test_login_invalid_city_id(session, valid_credentials):
    response = api_post(
        session,
        "/api/v1/auth/login/",
        json={
            "user_id": valid_credentials["user_id"],
            "password": valid_credentials["password"],
            "city_id": -1,
        },
    )

    assert response.status_code == 401


def test_login_invalid_user(session, valid_credentials):
    response = api_post(
        session,
        "/api/v1/auth/login/",
        json={
            "user_id": "-1",
            "password": valid_credentials["password"],
            "city_id": valid_credentials["city_id"],
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"user_id": ""},
        {"password": ""},
        {"city_id": ""},
        {"user_id": 123, "password": True, "city_id": 1000},
        {"user_id": None, "password": None, "city_id": None},
        {"user_id": "a" * 1000, "password": "b" * 1000, "city_id": 2**100},
    ],
)
def test_login_bad_input(session, payload):
    response = api_post(session, "/api/v1/auth/login/", json=payload)

    assert response.status_code in (401, 422)
