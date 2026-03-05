import pytest
import requests
from config import get_api_settings


settings = get_api_settings()

BASE_URL = f"http://{settings.HOST}:{settings.PORT}"
TEST_USER_ID = "1"
TEST_USER_PASSWORD = "1"
TEST_DELAY = 1
TIMEOUT = 5


class TestSession(requests.Session):
    def request(self, method, url, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = TIMEOUT
        return super().request(method, url, *args, **kwargs)


@pytest.fixture
def session():
    s = TestSession()
    yield s
    s.close()


@pytest.fixture
def valid_credentials():
    return {
        "user_id": TEST_USER_ID,
        "password": TEST_USER_PASSWORD
    }

@pytest.fixture
def auth_headers(session, valid_credentials) -> dict[str, str]:
    response = session.post(f"{BASE_URL}/api/v1/auth/login/", json=valid_credentials)
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def assert_schema(data: dict, schema: dict) -> None:
    for key, expected_type in schema.items():
        assert key in data, f"Missing key: {key}"
        assert isinstance(data[key], expected_type), \
            f"Field '{key}' expected {expected_type.__name__}, got {type(data[key]).__name__}"