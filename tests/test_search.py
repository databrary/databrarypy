"""Tests for SearchResource."""

from databrarypy.client import DatabraryClient

from .fixtures.search import build_composite_transport


def _make_client():
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
    return client


def test_search_users():
    client = _make_client()
    page = client.search.users("alex", filter="active", page=1, page_size=20, sort_by="name")
    assert page.count == 1
    hit = page.results[0]
    assert hit.full_name == "Alex Doe"
    assert hit.is_authorized is True


def test_search_institutions():
    client = _make_client()
    page = client.search.institutions("Example", page=2, page_size=5, sort_order="desc")
    assert page.count == 1
    hit = page.results[0]
    assert hit.name == "Example University"


def test_search_volumes():
    client = _make_client()
    page = client.search.volumes(
        "language",
        files_release_levels=["public"],
        tag="language",
        sharing_level="public",
        format_categories=["Audio"],
        formats=["audio/mpeg"],
        page=1,
        page_size=10,
        sort_by="score",
        sort_order="desc",
    )
    assert page.count == 1
    hit = page.results[0]
    assert hit.title == "Language Development"
    assert hit.owner.full_name == "Alex Doe"
