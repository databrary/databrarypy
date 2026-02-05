from __future__ import annotations

import pytest
from tests.conftest import collect_items, first_page_item

from databrarypy.client import DatabraryClient


def _first_volume_id(client: DatabraryClient) -> int:
    vols = client.volumes.page(page=1)
    first_vol = first_page_item(vols)
    if first_vol is None:
        pytest.skip("No volumes available to test folders")
    return first_vol.id


def test_folders_list_and_retrieve(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.folders.page(vid, page=1)
    assert page.count >= 0
    next_folder = first_page_item(page)
    if next_folder is None:
        pytest.skip("No folders available to test folders")
    folder = client.folders.retrieve(vid, next_folder.id)
    assert folder.id == next_folder.id


def test_folders_files(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.folders.page(vid, page=1)
    next_folder = first_page_item(page)
    if next_folder is None:
        pytest.skip("No folders available to test folders")
    fid = next_folder.id

    files = client.folders.files_page(vid, fid, page=1)
    if files.count == 0:
        pytest.skip("No files in folders fixtures")
    assert files.count == len(files.results)


def test_folders_iterators(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.folders.page(vid, page=1)
    next_folder = first_page_item(page)
    if next_folder is None:
        pytest.skip("No folders available to test folders")
    fid = next_folder.id
    seen_items = collect_items(client.folders.files_list(vid, fid, page=1, page_size=5), limit=6)
    assert seen_items and len(seen_items) <= 6


def test_folders_list_iterator(client: DatabraryClient):
    vid = _first_volume_id(client)
    seen_items = collect_items(client.folders.list(vid, page=1, page_size=5), limit=6)
    assert seen_items and len(seen_items) <= 6


def test_folders_get_single_file(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.folders.page(vid, page=1)
    next_folder = first_page_item(page)
    if next_folder is None:
        pytest.skip("No folders available to test folders")
    fid = next_folder.id
    files = client.folders.files_page(vid, fid, page=1)
    if files.count == 0:
        pytest.skip("No files in folders fixtures")
    assert files.count > 0
    next_file = first_page_item(files)
    if next_file is None:
        pytest.skip("No files available to test files")
    file_id = next_file.id
    f = client.folders.get_file(vid, fid, file_id)
    assert f.id == file_id
