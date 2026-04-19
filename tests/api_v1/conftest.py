import datetime as dt
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
import requests
from config import get_api_settings
from loguru import logger
from sqlalchemy import Result

from core.api_v1.auth.hashing import hash_password
from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import (
    Event,
    Item,
    Link,
    Report,
    User,
    UserEvent,
    UserItem,
)


settings = get_api_settings()

BASE_URL = f"http://{settings.HOST}:{settings.PORT}"
TEST_DELAY = 1
TEST_USER_CITY_ID = 1
TEST_USER_POINTS: str = "1000"
TIMEOUT = 5


class TestSession(requests.Session):
    def request(self, method, url, *args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = TIMEOUT
        return super().request(method, url, *args, **kwargs)


@pytest.fixture
def session():
    s = TestSession()
    yield s
    s.close()


@pytest.fixture(scope="session", autouse=True)
def silence_loguru_for_pytest():
    logger.remove()
    yield


def api_url(path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{BASE_URL}{normalized_path}"


def api_request(session, method: str, path: str, **kwargs):
    return session.request(method=method, url=api_url(path), **kwargs)


def api_get(session, path: str, **kwargs):
    return api_request(session, "GET", path, **kwargs)


def api_post(session, path: str, **kwargs):
    return api_request(session, "POST", path, **kwargs)


def api_patch(session, path: str, **kwargs):
    return api_request(session, "PATCH", path, **kwargs)


def api_delete(session, path: str, **kwargs):
    return api_request(session, "DELETE", path, **kwargs)


def login(session, credentials):
    return api_post(session, "/api/v1/auth/login/", json=credentials)


def assert_token_response(response) -> dict:
    assert response.status_code == 200
    body = response.json()
    assert_schema(body, {"token": str, "token_type": str})
    assert body["token_type"] == "access"
    return body


def assert_refresh_cookie(session) -> str:
    refresh_token = session.cookies.get("refresh_token")
    assert refresh_token is not None
    assert refresh_token != ""
    return refresh_token


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def valid_credentials():
    password = f"pytest-password-{uuid4().hex}"
    user = User(
        full_name=f"Pytest User {uuid4().hex[:8]}",
        birth=dt.date(1995, 1, 1),
        passport=f"pytest-passport-{uuid4().hex}",
        phone_number=f"+7999{uuid4().int % 10**7:07d}",
        points=TEST_USER_POINTS,
        password=hash_password(password),
        telegram_id=None,
        city_id=TEST_USER_CITY_ID,
    )
    await CRUD.add(user).execute()
    credentials = {
        "user_id": str(user.id),
        "city_id": str(user.city_id),
        "password": password,
    }
    yield credentials

    user_id = user.id
    await CRUD.delete(UserEvent).where(UserEvent.user_id == user_id).execute()
    await CRUD.delete(UserItem).where(UserItem.user_id == user_id).execute()
    await CRUD.delete(Report).where(Report.user_id == user_id).execute()
    await (
        CRUD.update(Link).where(Link.user_id == user_id).values(user_id=None).execute()
    )
    await CRUD.delete(User).where(User.id == user_id).execute()


@pytest.fixture
def auth_headers(session, valid_credentials) -> dict[str, str]:
    response = login(session, valid_credentials)
    token = assert_token_response(response)["token"]
    return {"Authorization": f"Bearer {token}"}


def assert_schema(data: dict, schema: dict) -> None:
    for key, expected_type in schema.items():
        assert key in data, f"Missing key: {key}"
        assert isinstance(data[key], expected_type), (
            f"Field '{key}' expected {expected_type.__name__}, got {type(data[key]).__name__}"
        )


def assert_error_detail(response, expected_detail: str) -> None:
    body = response.json()
    assert "detail" in body, f"Response has no 'detail': {body}"
    assert body["detail"] == expected_detail


def assert_no_content(response, expected_status_code: int) -> None:
    assert response.status_code == expected_status_code
    assert response.text == ""


def assert_validation_error(response) -> None:
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)


@pytest.fixture(scope="session")
def current_user_id(valid_credentials) -> int:
    return int(valid_credentials["user_id"])


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def another_user(current_user_id) -> User | None:
    users_query_result: Result = (
        await CRUD.get(User).where(User.id != current_user_id).execute()
    )
    return users_query_result.scalars().first()


@pytest.fixture
def create_item():
    async def factory(
        *,
        name: str | None = None,
        image_url: str = "https://example.com/item.png",
        price: Decimal = Decimal("1"),
        amount: int = 1,
    ) -> Item:
        item = Item(
            name=name or f"pytest-item-{uuid4().hex}",
            image_url=image_url,
            price=price,
            amount=amount,
        )
        await CRUD.add(item).execute()
        return item

    return factory


@pytest.fixture
def create_event():
    async def factory(
        *, name: str, description: str, points: Decimal, datetime
    ) -> Event:
        event = Event(
            name=name, description=description, points=points, datetime=datetime
        )
        await CRUD.add(event).execute()
        return event

    return factory


@pytest.fixture
def create_link():
    async def factory(
        *,
        link: str | None = None,
        is_prohibited=None,
        priority: float | None = 1,
        user_id: int | None = None,
    ) -> Link:
        link_model = Link(
            link=link or f"https://pytest-link-{uuid4().hex}.example.com/",
            is_prohibited=is_prohibited,
            priority=priority,
            user_id=user_id,
        )
        await CRUD.add(link_model).execute()
        return link_model

    return factory


@pytest.fixture
def create_report():
    async def factory(
        *,
        title: str | None = None,
        description: str = "Created by automated API test",
        user_id: int,
        status=None,
    ) -> Report:
        report = Report(
            title=title or f"pytest-report-{uuid4().hex}",
            description=description,
            user_id=user_id,
            status=status,
        )
        await CRUD.add(report).execute()
        return report

    return factory
