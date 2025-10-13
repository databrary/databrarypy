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
