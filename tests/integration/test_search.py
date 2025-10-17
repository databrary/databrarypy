from __future__ import annotations

from databrarypy.client import DatabraryClient


def test_search_users(client: DatabraryClient):
    page = client.search.users_page(q="a", page=1)
    assert page.count >= 0
    users = list(client.search.users_list(q="a", page=1, page_size=5))
    assert len(users) >= 0


def test_search_institutions(client: DatabraryClient):
    page = client.search.institutions_page(q="a", page=1)
    assert page.count >= 0
    insts = list(client.search.institutions_list(q="a", page=1, page_size=5))
    assert len(insts) >= 0


def test_search_volumes(client: DatabraryClient):
    page = client.search.volumes_page(q="a", page=1)
    assert page.count >= 0
    # Exercise filters; values are generic so backend may return empty but should accept params
    with_filters = client.search.volumes_page(
        q="a",
        files_release_levels=["authorized_users"],
        format_categories=["Video"],
        formats=["mp4"],
        page=1,
        page_size=5,
    )
    assert with_filters.count >= 0


def test_search_volumes_list_with_filters(client: DatabraryClient):
    seen = []
    for idx, v in enumerate(
        client.search.volumes_list(
            q="a",
            files_release_levels=["authorized_users"],
            format_categories=["Video"],
            formats=["mp4"],
            page=1,
            page_size=5,
        )
    ):
        seen.append(v)
        if idx > 5:
            break
    assert isinstance(seen, list)
    vols = list(client.search.volumes_list(q="a", page=1, page_size=5))
    assert len(vols) >= 0
