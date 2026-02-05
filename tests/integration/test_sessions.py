from __future__ import annotations

import pytest
from tests.conftest import collect_items, first_page_item

from databrarypy.client import DatabraryClient


def _first_volume_id(client: DatabraryClient) -> int:
    vols = client.volumes.page(page=1)
    first_vol = first_page_item(vols)
    if first_vol is None:
        pytest.skip("No volumes available to test sessions")
    return first_vol.id


def test_sessions_list_and_retrieve(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.sessions.page(vid, page=1)
    assert page.count >= 0
    next_element = first_page_item(page)
    if next_element is None:
        pytest.skip("No sessions available to test sessions")
    sess = client.sessions.retrieve(vid, next_element.id)
    assert sess.id == next_element.id


def test_sessions_files(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.sessions.page(vid, page=1)
    next_element = first_page_item(page)
    if next_element is None:
        pytest.skip("No sessions available to test sessions")
    sid = next_element.id

    files = client.sessions.files_page(vid, sid, page=1)
    if files.count == 0:
        pytest.skip("No session files in fixture")
    assert files.count == len(files.results)


def test_sessions_iterators(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.sessions.page(vid, page=1)
    next_element = first_page_item(page)
    if next_element is None:
        pytest.skip("No sessions available to test sessions")
    sid = next_element.id
    seen_items = collect_items(client.sessions.files_list(vid, sid, page=1, page_size=5), limit=6)
    assert len(seen_items) <= 6


def test_sessions_list_iterator(client: DatabraryClient):
    vid = _first_volume_id(client)
    seen_items = collect_items(client.sessions.list(vid, page=1, page_size=5), limit=6)
    assert len(seen_items) <= 6


def test_sessions_get_single_file(client: DatabraryClient):
    vid = _first_volume_id(client)
    page = client.sessions.page(vid, page=1)
    next_element = first_page_item(page)
    if next_element is None:
        pytest.skip("No sessions available to test sessions")
    sid = next_element.id
    files = client.sessions.files_page(vid, sid, page=1)
    next_file = first_page_item(files)
    if next_file is None:
        pytest.skip("No files available to test files")
    f = client.sessions.get_file(vid, sid, next_file.id)
    assert f.id == next_file.id
