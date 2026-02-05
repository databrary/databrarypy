from __future__ import annotations

import pytest
from tests.conftest import first_page_item

from databrarypy.client import DatabraryClient


def test_records_list_and_retrieve(client: DatabraryClient):
    vols = client.volumes.page(page=1)
    first_volume = first_page_item(vols)
    if first_volume is None:
        pytest.skip("No volumes available to test records")
    page = client.records.page(first_volume.id, page=1)
    assert page.count >= 0
    next_record = first_page_item(page)
    if next_record is None:
        pytest.skip("No records available to test records")
    rec = client.records.retrieve(first_volume.id, next_record.id)
    assert rec.id == next_record.id
