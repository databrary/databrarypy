"""Tests for SearchResource."""

from databrarypy.client import DatabraryClient

from ..fixtures.search import (
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
        transport=transport,
    )
    client.auth.login()
    return client


def test_search_users():
    client = _make_client()
    page = client.search.users_page("alex", filter="active", page=1, page_size=20, sort_by="name")
    assert page.count == 1
    hit = page.results[0]
    expected = _get_mock_user_hit()
    assert hit.full_name == expected["full_name"]
    assert hit.is_authorized is True


def test_search_institutions():
    client = _make_client()
    page = client.search.institutions_page("Example", page=2, page_size=5, sort_order="desc")
    assert page.count == 1
    hit = page.results[0]
    expected = _get_mock_institution_hit()
    assert hit.name == expected["name"]


def test_search_volumes():
    client = _make_client()
    page = client.search.volumes_page(
        "language",
        files_release_levels=["public", "private"],
        tag="science",
        sharing_level="public",
        page=3,
        page_size=10,
        sort_by="title",
        sort_order="asc",
    )
    assert page.count == 1
    hit = page.results[0]
    expected = _get_mock_volume_hit()
    assert hit.title == expected["title"]
    assert hit.owner.full_name == expected["owner"]["full_name"]


def test_search_list_variants():
    client = _make_client()
    # users list
    users = list(
        client.search.users_list(
            q="alex", filter="active", page=1, page_size=5, sort_by="name", sort_order="asc"
        )
    )
    assert users and users[0].full_name == _get_mock_user_hit()["full_name"]
    # institutions list
    insts = list(
        client.search.institutions_list(q="Example", page=1, page_size=5, sort_order="desc")
    )
    assert insts and insts[0].name == _get_mock_institution_hit()["name"]
    # volumes list basic
    vols = list(
        client.search.volumes_list(
            q="lang", files_release_levels=["public"], tag="science", page=1, page_size=2
        )
    )
    assert vols and vols[0].id == _get_mock_volume_hit()["id"]


def test_search_volumes_page_with_format_lists():
    client = _make_client()
    # page variant with format_categories and formats
    page = client.search.volumes_page(
        q="lang", format_categories=["video"], formats=["mp4"], page=1, page_size=1
    )
    assert (
        page.count == 1
        and page.results[0].owner.full_name == _get_mock_volume_hit()["owner"]["full_name"]
    )
    # list variant with both as well
    vols = list(
        client.search.volumes_list(
            q="lang", format_categories=["image"], formats=["jpg"], page=1, page_size=1
        )
    )
    assert vols and vols[0].title == _get_mock_volume_hit()["title"]
