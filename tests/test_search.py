"""Tests for SearchResource."""

from databrarypy.client import DatabraryClient

from .fixtures.search import (
    _get_mock_institution_hit,
    _get_mock_user_hit,
    _get_mock_volume_hit,
    build_composite_transport,
)


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
    expected = _get_mock_user_hit()
    assert hit.full_name == expected["full_name"]
    assert hit.is_authorized is True


def test_search_institutions():
    client = _make_client()
    page = client.search.institutions("Example", page=2, page_size=5, sort_order="desc")
    assert page.count == 1
    hit = page.results[0]
    expected = _get_mock_institution_hit()
    assert hit.name == expected["name"]


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
    expected = _get_mock_volume_hit()
    assert hit.title == expected["title"]
    assert hit.owner.full_name == expected["owner"]["full_name"]
