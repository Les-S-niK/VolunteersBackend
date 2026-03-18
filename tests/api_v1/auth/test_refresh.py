from conftest import (
    TEST_DELAY,
    api_post,
    assert_refresh_cookie,
    assert_token_response,
    login,
)
from time import sleep


def test_refresh_success(session, valid_credentials):
    login_response = login(session, valid_credentials)
    assert_token_response(login_response)
    assert_refresh_cookie(session)

    refresh_response = api_post(session, "/api/v1/auth/refresh/")

    assert_token_response(refresh_response)


def test_refresh_without_refresh_token(session):
    response = api_post(session, "/api/v1/auth/refresh/")

    assert response.status_code == 401
    assert "refresh token" in response.json()["detail"].lower()


def test_refresh_with_invalid_refresh_token(session):
    session.cookies.set("refresh_token", "invalid.token.value")
    response = api_post(session, "/api/v1/auth/refresh/")

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_refresh_with_tampered_token(session, valid_credentials):
    login_response = login(session, valid_credentials)
    assert_token_response(login_response)

    original_token = assert_refresh_cookie(session)
    tampered_token = original_token[:-5] + "xxxxx"

    session.cookies.set("refresh_token", tampered_token)
    response = api_post(session, "/api/v1/auth/refresh/")

    assert response.status_code == 401


def test_refresh_returns_unique_tokens(session, valid_credentials):
    login_response = login(session, valid_credentials)
    assert_token_response(login_response)

    refresh_response1 = api_post(session, "/api/v1/auth/refresh/")
    token1 = assert_token_response(refresh_response1)["token"]

    sleep(TEST_DELAY)

    refresh_response2 = api_post(session, "/api/v1/auth/refresh/")
    token2 = assert_token_response(refresh_response2)["token"]

    assert token1 != token2


def test_refresh_returns_new_refresh_token_cookie(session, valid_credentials):
    login_response = login(session, valid_credentials)
    assert_token_response(login_response)
    old_refresh_token = assert_refresh_cookie(session)

    sleep(TEST_DELAY)
    refresh_response = api_post(session, "/api/v1/auth/refresh/")
    assert_token_response(refresh_response)
    new_refresh_token = assert_refresh_cookie(session)

    assert old_refresh_token != new_refresh_token


def test_refresh_multiple_times_in_sequence(session, valid_credentials):
    login_response = login(session, valid_credentials)
    assert_token_response(login_response)

    for _ in range(8):
        response = api_post(session, "/api/v1/auth/refresh/")
        assert_token_response(response)
        assert_refresh_cookie(session)


def test_refresh_returns_access_token_type(session, valid_credentials):
    login_response = login(session, valid_credentials)
    assert_token_response(login_response)

    refresh_response = api_post(session, "/api/v1/auth/refresh/")

    assert_token_response(refresh_response)


def test_refresh_empty_cookie_value(session):
    session.cookies.set("refresh_token", "")
    response = api_post(session, "/api/v1/auth/refresh/")

    assert response.status_code == 401


def test_refresh_with_whitespace_token(session):
    session.cookies.set("refresh_token", "   ")
    response = api_post(session, "/api/v1/auth/refresh/")

    assert response.status_code == 401
