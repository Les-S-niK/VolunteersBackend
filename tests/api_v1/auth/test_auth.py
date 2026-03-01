from conftest import BASE_URL, TEST_USER_ID, TEST_DELAY
from time import sleep
import pytest



# Tests for POST /api/v1/auth/login/ endpoint 

def test_login_success(session, valid_credentials):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert response.status_code == 200
    
    body = response.json()
    
    assert "token" in body
    assert isinstance(body["token"], str)
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


def test_login_invalid_password(session):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json={"user_id": TEST_USER_ID, "password": "wrong"}
    )

    assert response.status_code == 401
    assert response.status_code != 500


def test_login_invalid_user(session):
    response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json={"user_id": "0", "password": "wrong"}
    )

    assert response.status_code == 401
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


# Tests for POST /api/v1/auth/refresh/ endpoint 

def test_refresh_success(session, valid_credentials):
    login_response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert login_response.status_code == 200
    assert "refresh_token" in session.cookies.get_dict()
    
    refresh_response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert refresh_response.status_code == 200
    assert "token" in refresh_response.json()


def test_refresh_without_refresh_token(session):
    response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert response.status_code == 401
    assert "refresh token" in response.json()["detail"].lower()


def test_refresh_with_invalid_refresh_token(session):
    session.cookies.set("refresh_token", "invalid.token.value")
    response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_refresh_with_tampered_token(session, valid_credentials):
    login_response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert login_response.status_code == 200
    
    original_token = session.cookies.get("refresh_token")
    tampered_token = original_token[:-5] + "xxxxx"
    
    session.cookies.set("refresh_token", tampered_token)
    response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert response.status_code == 401


def test_refresh_returns_unique_tokens(session, valid_credentials):
    login_response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert login_response.status_code == 200
    
    refresh_response1 = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    assert refresh_response1.status_code == 200
    token1 = refresh_response1.json()["token"]
    
    sleep(TEST_DELAY)
    
    refresh_response2 = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    assert refresh_response2.status_code == 200
    token2 = refresh_response2.json()["token"]
    
    assert token1 != token2


def test_refresh_returns_new_refresh_token_cookie(session, valid_credentials):
    login_response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert login_response.status_code == 200
    old_refresh_token = session.cookies.get("refresh_token")
    
    sleep(TEST_DELAY)
    refresh_response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert refresh_response.status_code == 200
    new_refresh_token = session.cookies.get("refresh_token")
    
    assert new_refresh_token is not None
    assert old_refresh_token != new_refresh_token


def test_refresh_multiple_times_in_sequence(session, valid_credentials):
    login_response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert login_response.status_code == 200
    
    for i in range(8):
        response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
        assert response.status_code == 200
        assert "token" in response.json()
        assert "refresh_token" in session.cookies.get_dict()
        sleep(0.2)


def test_refresh_returns_access_token_type(session, valid_credentials):
    login_response = session.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=valid_credentials
    )
    assert login_response.status_code == 200
    
    refresh_response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert "token" in body
    assert "token_type" in body
    assert body["token_type"] == "access"


def test_refresh_empty_cookie_value(session):
    session.cookies.set("refresh_token", "")
    response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert response.status_code == 401


def test_refresh_with_whitespace_token(session):
    session.cookies.set("refresh_token", "   ")
    response = session.post(f"{BASE_URL}/api/v1/auth/refresh/")
    
    assert response.status_code == 401