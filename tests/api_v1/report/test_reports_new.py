import pytest
from conftest import api_post, assert_no_content, assert_validation_error
from sqlalchemy import Result
from uuid import uuid4

from core.database.sqlalchemy.db import CRUD
from core.database.sqlalchemy.models import Report, ReportStatuses


def test_post_new_report_unauthorized(session):
    response = api_post(
        session,
        "/api/v1/reports/new/",
        json={
            "title": "Unauthorized report",
            "description": "Should not be created without auth",
        },
    )

    assert response.status_code == 401


def test_post_new_report_validation_error_missing_description(
    session, auth_headers
):
    response = api_post(
        session,
        "/api/v1/reports/new/",
        json={"title": "Missing description"},
        headers=auth_headers,
    )

    assert_validation_error(response)


def test_post_new_report_validation_error_missing_title(session, auth_headers):
    response = api_post(
        session,
        "/api/v1/reports/new/",
        json={"description": "Missing title"},
        headers=auth_headers,
    )

    assert_validation_error(response)


def test_post_new_report_validation_error_empty_body(session, auth_headers):
    response = api_post(
        session,
        "/api/v1/reports/new/",
        json={},
        headers=auth_headers,
    )

    assert_validation_error(response)


@pytest.mark.asyncio(loop_scope="session")
async def test_post_new_report_success_creates_report(
    session, auth_headers, current_user_id
):
    title = f"pytest-report-{uuid4().hex}"
    description = "Created by automated API test"

    try:
        response = api_post(
            session,
            "/api/v1/reports/new/",
            json={"title": title, "description": description},
            headers=auth_headers,
        )

        assert_no_content(response, 201)

        report_query_result: Result = (
            await CRUD.get(Report)
            .where(Report.title == title)
            .where(Report.description == description)
            .where(Report.user_id == current_user_id)
            .execute()
        )
        report: Report | None = report_query_result.scalar_one_or_none()

        assert report is not None
        assert report.status == ReportStatuses.unanswered
    finally:
        await CRUD.delete(Report).where(Report.title == title).execute()
