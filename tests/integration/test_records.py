from __future__ import annotations

from contextlib import suppress

import pytest
from tests.conftest import first_page_item
from tests.integration.conftest import unique_name

from databrarypy.client import DatabraryClient
from databrarypy.errors import NotFoundError
from databrarypy.models.bulk import BulkItemStatus


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


def test_records_create_update_delete_lifecycle(
    client: DatabraryClient,
    writable_volume: int,
    integration_category_id: int,
):
    """Full CRUD lifecycle: create -> retrieve -> update -> delete."""
    record = client.records.create(
        writable_volume,
        category_id=integration_category_id,
        name=unique_name("integ-record"),
    )
    assert record.id > 0
    assert record.volume == writable_volume
    assert record.category_id == integration_category_id

    retrieved = client.records.retrieve(writable_volume, record.id)
    assert retrieved.id == record.id

    try:
        merged_measures = {**retrieved.measures, "30": "Updated value"}
        updated = client.records.update(
            writable_volume,
            record.id,
            measures=merged_measures,
        )
        assert updated.id == record.id
    finally:
        deleted = client.records.delete(writable_volume, record.id)
        assert deleted is True


def test_records_create_with_extra_measures(
    client: DatabraryClient,
    writable_volume: int,
    integration_category_id: int,
):
    record = client.records.create(
        writable_volume,
        category_id=integration_category_id,
        name=unique_name("integ-measures"),
        measures={"30": "Extra value"},
    )
    assert record.id > 0
    assert record.measures is not None

    client.records.delete(writable_volume, record.id)


def test_records_set_and_delete_measure(
    client: DatabraryClient,
    writable_volume: int,
    integration_category_id: int,
):
    """Create a record, set a measure on it, then delete the measure."""
    record = client.records.create(
        writable_volume,
        category_id=integration_category_id,
        name=unique_name("measure-test"),
    )
    assert record.id > 0

    try:
        vol_detail = client.volumes.retrieve(writable_volume)
        category = next(
            (c for c in vol_detail.enabled_categories if c.id == integration_category_id),
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
            writable_volume, record.id, metric.id, value="test value"
        )
        assert measure_data is not None

        deleted = client.records.delete_measure(writable_volume, record.id, metric.id)
        assert deleted is True
    finally:
        client.records.delete(writable_volume, record.id)


def test_records_list_by_category(
    client: DatabraryClient,
    integration_volume_id: int,
    integration_category_id: int,
):
    page = client.records.page(integration_volume_id, category_id=integration_category_id)
    assert page.count >= 0


def test_records_bulk_create_rename_delete(
    client: DatabraryClient,
    writable_volume: int,
    integration_category_id: int,
):
    names = [unique_name("bulk-a"), unique_name("bulk-b")]
    created_ids: list[int] = []

    try:
        bulk_create = client.records.bulk_create(
            writable_volume,
            integration_category_id,
            [{"name": n} for n in names],
        )
        assert len(bulk_create.succeeded) == 2
        assert all(item.status == BulkItemStatus.SUCCESS for item in bulk_create.items)
        created_ids = [item.result.id for item in bulk_create.succeeded]

        rename_pairs = [(created_ids[0], unique_name("bulk-renamed"))]
        bulk_rename = client.records.bulk_rename(
            writable_volume,
            integration_category_id,
            rename_pairs,
        )
        assert len(bulk_rename.succeeded) == 1

        bulk_delete = client.records.bulk_delete(writable_volume, created_ids)
        assert len(bulk_delete.succeeded) == 2
        created_ids = []
    finally:
        for rid in created_ids:
            with suppress(Exception):
                client.records.delete(writable_volume, rid)


def test_records_set_measure_not_found_mapping(
    client: DatabraryClient,
    writable_volume: int,
):
    with pytest.raises(NotFoundError, match="Failed to load record"):
        client.records.set_measure(writable_volume, 999_999_999, 1, value="x")
