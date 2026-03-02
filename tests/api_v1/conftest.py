import pytest
import requests
from config import get_api_settings


settings = get_api_settings()

BASE_URL = f"http://{settings.HOST}:{settings.PORT}"
TEST_USER_ID = "1"
TEST_USER_PASSWORD = "1"
TEST_DELAY = 1

@pytest.fixture
def session():
    s = requests.Session()
    yield s
    s.close()

@pytest.fixture
def valid_credentials():
    return {
        "user_id": TEST_USER_ID,
        "password": TEST_USER_PASSWORD
    }
