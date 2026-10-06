from __future__ import annotations

from pathlib import Path

import pytest
from tests.conftest import collect_items, first_page_item

from databrarypy.client import DatabraryClient
from databrarypy.models import InstitutionStatistics


def test_institutions_list_and_retrieve(client: DatabraryClient):
    page = client.institutions.page(page=1)
    assert page.count >= 0
    next_item = first_page_item(page)
    if next_item is None:
        pytest.skip("No institutions available to test institutions")
    inst = client.institutions.retrieve(next_item.id)
    assert inst.id == next_item.id


def test_institutions_iterators(client: DatabraryClient):
    seen_items = collect_items(client.institutions.list(page=1, page_size=5), limit=6)
    assert len(seen_items) <= 6


def test_institutions_avatar_and_investigators(client: DatabraryClient):
    page = client.institutions.page(page=1)
    next_item = first_page_item(page)
    if next_item is None:
        pytest.skip("No institutions available to test institutions")

    # Avatar may be missing; ensure call works
    data = client.institutions.avatar(next_item.id)
    assert isinstance(data, (bytes, str))

    # Investigators derived client-side from affiliates
    investigators = collect_items(
        client.institutions.authorized_investigators(next_item.id, page=1), limit=6
    )
    assert len(investigators) <= 6


def test_institutions_statistics(client: DatabraryClient):
    page = client.institutions.page(page=1)
    next_item = first_page_item(page)
    if next_item is None:
        pytest.skip("No institutions available to test statistics")

    stats = client.institutions.statistics(next_item.id)
    assert stats is None or isinstance(stats, InstitutionStatistics)


def test_institutions_avatar_dest_path(client: DatabraryClient, tmp_path: Path):
    page = client.institutions.page(page=1)
    next_item = first_page_item(page)
    if next_item is None:
        pytest.skip("No institutions available to test avatar download")

    dest = tmp_path / "inst-avatar.png"
    saved = client.institutions.avatar(next_item.id, dest_path=str(dest))
    assert isinstance(saved, str)
