from conftest import api_patch, assert_no_content, assert_token_response, login


def test_change_password_success(session, valid_credentials):
    login_response = login(session, valid_credentials)
    token = assert_token_response(login_response)["token"]
    headers = {"Authorization": f"Bearer {token}"}

    old_password = valid_credentials["password"]
    new_password = "NewStrongestPassword4321"

    payload = {
        "old_password": old_password,
        "new_password": new_password,
    }
    response = api_patch(
        session,
        "/api/v1/auth/change_password/",
        json=payload,
        headers=headers,
    )
    assert_no_content(response, 204)

    old_creds = {
        "user_id": valid_credentials["user_id"],
        "password": old_password,
        "city_id": valid_credentials["city_id"],
    }
    login_response_fail = login(session, old_creds)
    assert login_response_fail.status_code == 401

    new_credentials = {
        "user_id": valid_credentials["user_id"],
        "password": new_password,
        "city_id": valid_credentials["city_id"],
    }
    login_response_new = login(session, new_credentials)
    assert_token_response(login_response_new)

    login_after_change = login(session, new_credentials)
    token2 = assert_token_response(login_after_change)["token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    restore_payload = {
        "old_password": new_password,
        "new_password": old_password,
    }
    restore_response = api_patch(
        session,
        "/api/v1/auth/change_password/",
        json=restore_payload,
        headers=headers2,
    )
    assert_no_content(restore_response, 204)


def test_change_password_wrong_old_password(session, valid_credentials):
    login_response = login(session, valid_credentials)
    token = assert_token_response(login_response)["token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "old_password": "WrongPassword123",
        "new_password": "NewStrongestPassword4321",
    }
    response = api_patch(
        session,
        "/api/v1/auth/change_password/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 403


def test_change_password_unauthorized_without_token(session):
    payload = {
        "old_password": "OldStrongPassword1234",
        "new_password": "NewStrongestPassword4321",
    }
    response = api_patch(
        session,
        "/api/v1/auth/change_password/",
        json=payload,
    )
    assert response.status_code == 401


def test_change_password_unauthorized_with_invalid_token(session):
    headers = {"Authorization": "Bearer invalid-token"}
    payload = {
        "old_password": "OldStrongPassword1234",
        "new_password": "NewStrongestPassword4321",
    }
    response = api_patch(
        session,
        "/api/v1/auth/change_password/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 401


def test_change_password_same_as_old(session, valid_credentials):
    login_response = login(session, valid_credentials)
    token = assert_token_response(login_response)["token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "old_password": valid_credentials["password"],
        "new_password": valid_credentials["password"],
    }
    response = api_patch(
        session,
        "/api/v1/auth/change_password/",
        json=payload,
        headers=headers,
    )
    assert_no_content(response, 204)
