"""Tests for FundersResource."""

from databrarypy.client import DatabraryClient

from ..fixtures.constants import (
    TEST_BASE_URL,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)
from ..fixtures.funders import build_composite_transport


def test_funders_list_and_retrieve():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    items = client.funders.list(is_approved=True)
    assert len(items) == 2
    assert items[0].name

    funder = client.funders.retrieve(items[0].id)
    assert funder.id == items[0].id


def test_funders_list_include_all_param_only_when_true():
    # Build a transport that captures the request URL for the funders list call
    import httpx

    from ..fixtures.auth import handle_token_success
    from ..fixtures.common import build_transport

    captured = {"url": None}

    def handle_funders(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"count": 0, "next": None, "previous": None, "results": []})

    transport = build_transport(
        ("POST", "/o/token/", handle_token_success),
        ("GET", "/funders/", handle_funders),
    )

    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    # include_all=False should NOT include all=true
    client.funders.list(include_all=False)
    assert captured["url"] == f"{TEST_BASE_URL}/funders/"

    # include_all=True should include all=true
    client.funders.list(include_all=True)
    assert captured["url"].startswith(f"{TEST_BASE_URL}/funders/?")
    assert "all=true" in captured["url"]
