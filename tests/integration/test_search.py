from __future__ import annotations

from databrarypy.client import DatabraryClient


def test_search_users(client: DatabraryClient):
    page = client.search.users_page(q="a", page=1)
    assert page.count >= 0


def test_search_institutions(client: DatabraryClient):
    page = client.search.institutions_page(q="a", page=1)
    assert page.count >= 0


def test_search_volumes(client: DatabraryClient):
    page = client.search.volumes_page(q="a", page=1)
    assert page.count >= 0
