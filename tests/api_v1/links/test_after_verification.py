import pytest
from conftest import BASE_URL

def test_patch_link_status_success(session, auth_headers):
    
    get_link_response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=auth_headers
    )
    
    if get_link_response.status_code == 204:
        pytest.skip("No unverified links available in database")
    
    assert get_link_response.status_code == 200
    link_url = get_link_response.json()["link"]
    
    patch_payload = {
        "link": link_url,
        "is_prohibited": True
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 204


def test_patch_link_status_forbidden_not_owner(session, auth_headers):
    get_link_response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=auth_headers
    )
    
    if get_link_response.status_code == 204:
        pytest.skip("No unverified links available in database")
    
    assert get_link_response.status_code == 200
    link_url = get_link_response.json()["link"]
    
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTkiLCJpYXQiOjE1MTYyMzkwMjJ9.invalid"
    headers_fake = {"Authorization": f"Bearer {fake_token}"}
    
    patch_payload = {
        "link": link_url,
        "is_prohibited": False
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload,
        headers=headers_fake
    )
    
    assert response.status_code == 401


def test_patch_link_not_found(session, auth_headers):
    patch_payload = {
        "link": "https://nonexistent-domain-12345.com",
        "is_prohibited": True
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body or "details" in body


def test_patch_link_validation_error_invalid_url(session, auth_headers):
    patch_payload = {
        "link": "not-a-valid-url",
        "is_prohibited": True
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 422


def test_patch_link_validation_error_missing_field(session, auth_headers):
    patch_payload = {
        "link": "https://example.com"
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 422


def test_patch_link_unauthorized_no_token(session):
    patch_payload = {
        "link": "https://example.com",
        "is_prohibited": True
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload
    )
    
    assert response.status_code == 401


def test_patch_link_false_value(session, auth_headers):
    get_link_response = session.patch(
        f"{BASE_URL}/api/v1/links/first_unverified/",
        headers=auth_headers
    )
    
    if get_link_response.status_code == 204:
        pytest.skip("No unverified links available in database")
    
    assert get_link_response.status_code == 200
    link_url = get_link_response.json()["link"]
    
    patch_payload = {
        "link": link_url,
        "is_prohibited": False
    }
    response = session.patch(
        f"{BASE_URL}/api/v1/links/after_verification/",
        json=patch_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 204
