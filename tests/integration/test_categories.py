from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def test_categories_list_and_retrieve(client: DatabraryClient):
    items = client.categories.list()
    assert isinstance(items, list)
    cid = items[0].id if items else None
    if cid is not None:
        cat = client.categories.retrieve(cid)
        assert cat.id == cid
