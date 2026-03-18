from conftest import (
    api_delete,
    api_post,
    assert_no_content,
    assert_token_response,
    login,
)


def test_logout_success(session, valid_credentials):
    login_response = login(session, valid_credentials)
    token = assert_token_response(login_response)["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = api_delete(session, "/api/v1/auth/logout/", headers=headers)

    assert_no_content(response, 204)
    set_cookie_header = response.headers.get("Set-Cookie", "")
    assert "refresh_token=" in set_cookie_header
    assert "Max-Age=0" in set_cookie_header or "expires=" in set_cookie_header.lower()


def test_logout_unauthorized_without_token(session):
    response = api_delete(session, "/api/v1/auth/logout/")

    assert response.status_code == 401


def test_logout_unauthorized_with_invalid_token(session):
    response = api_delete(
        session,
        "/api/v1/auth/logout/",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_logout_invalidates_access_token_for_reuse(session, valid_credentials):
    login_response = login(session, valid_credentials)
    token = assert_token_response(login_response)["token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = api_delete(session, "/api/v1/auth/logout/", headers=headers)

    assert_no_content(logout_response, 204)

    repeated_logout_response = api_delete(
        session,
        "/api/v1/auth/logout/",
        headers=headers,
    )

    assert repeated_logout_response.status_code == 401


def test_logout_removes_refresh_token_from_session(session, valid_credentials):
    login_response = login(session, valid_credentials)
    token = assert_token_response(login_response)["token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = api_delete(session, "/api/v1/auth/logout/", headers=headers)

    assert_no_content(logout_response, 204)

    refresh_response = api_post(session, "/api/v1/auth/refresh/")

    assert refresh_response.status_code == 401
