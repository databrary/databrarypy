"""Tests for FundersResource."""

from databrarypy.client import DatabraryClient

from .fixtures.funders import build_composite_transport


def test_funders_list_and_retrieve():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    page = client.funders.list(is_approved=True, page=1, page_size=50)
    assert page.count == 2
    assert page.results[0].name

    funder = client.funders.retrieve(page.results[0].id)
    assert funder.id == page.results[0].id


def test_funders_list_include_all_param_only_when_true():
    # Build a transport that captures the request URL for the funders list call
    import httpx

    from .fixtures.auth import handle_token_success
    from .fixtures.common import build_transport

    captured = {"url": None}

    def handle_funders(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"count": 0, "next": None, "previous": None, "results": []})

    transport = build_transport(
        ("POST", "/o/token/", handle_token_success),
        ("GET", "/funders/", handle_funders),
    )

    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login_with_password("user", "pass")

    # include_all=False should NOT include all=true
    client.funders.list(include_all=False)
    assert captured["url"] == "https://api.example/funders/"

    # include_all=True should include all=true
    client.funders.list(include_all=True)
    assert captured["url"].startswith("https://api.example/funders/?")
    assert "all=true" in captured["url"]
