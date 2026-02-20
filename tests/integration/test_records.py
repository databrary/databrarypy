from __future__ import annotations

import pytest
from tests.conftest import first_page_item

from databrarypy.client import DatabraryClient

VOLUME_ID = 1777
CATEGORY_ID_TASK = 6


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


def test_records_create_update_delete_lifecycle(client: DatabraryClient):
    """Full CRUD lifecycle: create -> retrieve -> update -> delete."""
    record = client.records.create(
        VOLUME_ID,
        category_id=CATEGORY_ID_TASK,
        name="Integration test record",
    )
    assert record.id > 0
    assert record.volume == VOLUME_ID
    assert record.category_id == CATEGORY_ID_TASK

    retrieved = client.records.retrieve(VOLUME_ID, record.id)
    assert retrieved.id == record.id

    try:
        merged_measures = {**retrieved.measures, "30": "Updated value"}
        updated = client.records.update(
            VOLUME_ID,
            record.id,
            measures=merged_measures,
        )
        assert updated.id == record.id
    finally:
        deleted = client.records.delete(VOLUME_ID, record.id)
        assert deleted is True


def test_records_create_with_extra_measures(client: DatabraryClient):
    record = client.records.create(
        VOLUME_ID,
        category_id=CATEGORY_ID_TASK,
        name="Task with measures",
        measures={"30": "Extra value"},
    )
    assert record.id > 0
    assert record.measures is not None

    client.records.delete(VOLUME_ID, record.id)


def test_records_set_and_delete_measure(client: DatabraryClient):
    """Create a record, set a measure on it, then delete the measure."""
    record = client.records.create(
        VOLUME_ID,
        category_id=CATEGORY_ID_TASK,
        name="Measure test record",
    )
    assert record.id > 0

    try:
        vol_detail = client.volumes.retrieve(VOLUME_ID)
        category = next(
            (c for c in vol_detail.enabled_categories if c.id == CATEGORY_ID_TASK),
            None,
        )
        if category is None:
            pytest.skip("Category not found in volume")

        optional_metrics = [
            m
            for m in category.metrics
            if not m.required and m.id in {em.id for em in vol_detail.enabled_metrics}
        ]
        if not optional_metrics:
            pytest.skip("No optional metrics available for measure tests")

        metric = optional_metrics[0]
        measure_data = client.records.set_measure(
            VOLUME_ID, record.id, metric.id, value="test value"
        )
        assert measure_data is not None

        deleted = client.records.delete_measure(VOLUME_ID, record.id, metric.id)
        assert deleted is True
    finally:
        client.records.delete(VOLUME_ID, record.id)


def test_records_list_by_category(client: DatabraryClient):
    page = client.records.page(VOLUME_ID, category_id=CATEGORY_ID_TASK)
    assert page.count >= 0
