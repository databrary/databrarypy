from __future__ import annotations

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
    assert len(tags) > 0

    links = client.volumes.links(next_volume.id)
    assert len(links) > 0

    fundings = client.volumes.fundings(next_volume.id)
    assert len(fundings) > 0


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
