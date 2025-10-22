from __future__ import annotations

import pytest
from tests.conftest import collect_items, first_list_item

from databrarypy.client import DatabraryClient


def test_iterate_volumes_users_and_records(client: DatabraryClient):
    # Volumes iterator yields at least first page size
    first_page = client.volumes.page(page=1, page_size=5)
    first_items = list(first_page.results)
    seen = collect_items(client.volumes.list(page=1, page_size=5), limit=10)

    first_ids = {item.id for item in first_items}
    seen_ids = {item.id for item in seen}

    assert first_ids.issubset(seen_ids)

    # Users iterator basic smoke
    u_first = client.users.page(page=1, page_size=5)
    u_seen = collect_items(client.users.list(page=1, page_size=5), limit=10)
    assert len(u_seen) == len(u_first.results)

    # Records iterator for first available volume
    next_element = first_list_item(first_page.results)
    if next_element is None:
        pytest.skip("No volumes available to test records")
    vid = next_element.id
    r_first = client.records.page(vid, page=1, page_size=2)
    r_seen = collect_items(client.records.list(vid, page=1, page_size=2), limit=5)
    assert len(r_seen) == len(r_first.results)
