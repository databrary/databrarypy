from __future__ import annotations

import pytest
from tests.conftest import collect_items, first_page_item

from databrarypy.client import DatabraryClient


def test_tags_list_and_retrieve(client: DatabraryClient):
    page = client.tags.page(page=1)
    assert page.count >= 0
    next_tag = first_page_item(page)
    if next_tag is None:
        pytest.skip("No tags available to test tags")
    tag = client.tags.retrieve(next_tag.id)
    assert tag.id == next_tag.id


def test_tags_iterators(client: DatabraryClient):
    seen_items = collect_items(client.tags.list(page=1, page_size=5), limit=6)
    assert len(seen_items) <= 6
