from __future__ import annotations

import pytest

from databrarypy.client import DatabraryClient


def test_funders_list_and_retrieve(client: DatabraryClient):
    items = client.funders.list(is_approved=True)
    assert len(items) >= 0
    next_item = next(iter(items), None)
    if next_item is None:
        pytest.skip("No funders available to test funders")
    funder = client.funders.retrieve(next_item.id)
    assert funder.id == next_item.id
