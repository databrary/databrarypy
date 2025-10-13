"""Tests for TagsResource."""

from databrarypy.client import DatabraryClient

from .fixtures.tags import build_composite_transport


def test_tags_list_and_retrieve():
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

    page = client.tags.list(search="lang", ordering="name")
    assert page.count == 1
    tag = page.results[0]
    assert tag.name == "language"

    detail = client.tags.retrieve(tag.id)
    assert detail.id == tag.id
