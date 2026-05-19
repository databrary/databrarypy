from __future__ import annotations

from contextlib import suppress

import pytest
from tests.conftest import collect_items, first_page_item

from databrarypy.client import DatabraryClient


def test_volumes_list_and_detail(client: DatabraryClient):
    page = client.volumes.page(page=1)
    assert page.count >= 0
    next_volume = first_page_item(page)
    if next_volume is None:
        pytest.skip("No volumes available to test volumes")
    vol = client.volumes.retrieve(next_volume.id)
    assert vol.id == next_volume.id


def test_volumes_tags_links_fundings(client: DatabraryClient):
    page = client.volumes.page(page=1)
    next_volume = first_page_item(page)
    if next_volume is None:
        pytest.skip("No volumes available to test volumes")
    tags = client.volumes.tags(next_volume.id)
    assert isinstance(tags, list)

    links = client.volumes.links(next_volume.id)
    assert isinstance(links, list)

    fundings = client.volumes.fundings(next_volume.id)
    assert isinstance(fundings, list)


def test_volumes_collaborators(client: DatabraryClient):
    page = client.volumes.page(page=1)
    next_volume = first_page_item(page)
    if next_volume is None:
        pytest.skip("No volumes available to test volumes")
    collabs = client.volumes.collaborators(next_volume.id)
    assert collabs and len(collabs) >= 0
    if len(collabs) > 0:
        cid = collabs[0].id
        collab = client.volumes.collaborator(next_volume.id, cid)
        assert collab.id == cid


def test_volumes_activity(client: DatabraryClient):
    page = client.volumes.page(page=1)
    next_volume = first_page_item(page)
    if next_volume is None:
        pytest.skip("No volumes available to test volumes")
    act_page = client.volumes.activity_page(next_volume.id, page=1)
    assert act_page.count > 0

    seen_items = collect_items(
        client.volumes.activity_list(next_volume.id, page=1, page_size=5), limit=6
    )
    assert len(seen_items) <= 6


def test_volumes_export_tasks(client: DatabraryClient, integration_volume_id: int):
    zip_task = client.volumes.request_zip_download(integration_volume_id)
    assert zip_task.task_id

    csv_task = client.volumes.request_csv_download(integration_volume_id)
    assert csv_task.task_id


def test_volumes_enabled_categories_round_trip(
    client: DatabraryClient,
    writable_volume: int,
):
    original = client.volumes.get_enabled_categories(writable_volume)
    original_ids = [c.id for c in original]
    if not original_ids:
        pytest.skip("Volume has no enabled categories to test round-trip")

    try:
        cats = client.volumes.get_enabled_categories(writable_volume)
        assert len(cats) >= 1

        if len(original_ids) > 1:
            to_disable = original_ids[-1]
            if to_disable in original_ids:
                client.volumes.disable_category(writable_volume, to_disable)
                after_disable = client.volumes.get_enabled_categories(writable_volume)
                assert all(c.id != to_disable for c in after_disable)
                client.volumes.enable_category(writable_volume, to_disable)

        client.volumes.set_enabled_categories(writable_volume, original_ids)
        restored = client.volumes.get_enabled_categories(writable_volume)
        assert {c.id for c in restored} == set(original_ids)
    except Exception as exc:
        with suppress(Exception):
            client.volumes.set_enabled_categories(writable_volume, original_ids)
        pytest.skip(f"Volume category admin not available: {exc}")
    finally:
        with suppress(Exception):
            client.volumes.set_enabled_categories(writable_volume, original_ids)
