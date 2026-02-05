from __future__ import annotations

from databrarypy.client import DatabraryClient


def test_categories_list_and_retrieve(client: DatabraryClient):
    items = client.categories.list()
    assert len(items) >= 0
    next_item = next(iter(items), None)
    if next_item is not None:
        cat = client.categories.retrieve(next_item.id)
        assert cat.id == next_item.id
