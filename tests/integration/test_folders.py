from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def _first_volume_id(client: DatabraryClient) -> int | None:
    vols = client.volumes.page(page=1)
    return _first_id(vols)


def test_folders_list_and_retrieve(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.folders.page(vid, page=1)
    assert page.count >= 0
    fid = _first_id(page)
    if fid is not None:
        folder = client.folders.retrieve(vid, fid)
        assert folder.id == fid


def test_folders_files_and_downloads(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.folders.page(vid, page=1)
    if not page.results:
        return
    fid = page.results[0].id

    files = client.folders.files_page(vid, fid, page=1)
    assert files.count >= 0


def test_folders_iterators(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.folders.page(vid, page=1)
    if not page.results:
        return
    fid = page.results[0].id
    seen = []
    for idx, f in enumerate(client.folders.files_list(vid, fid, page=1, page_size=5)):
        seen.append(f)
        if idx > 5:
            break
    assert isinstance(seen, list)


def test_folders_list_iterator(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    seen = []
    for idx, folder in enumerate(client.folders.list(vid, page=1, page_size=5)):
        seen.append(folder)
        if idx > 5:
            break
    assert isinstance(seen, list)


def test_folders_get_single_file(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.folders.page(vid, page=1)
    if not page.results:
        return
    fid = page.results[0].id
    files = client.folders.files_page(vid, fid, page=1)
    if not files.results:
        return
    file_id = files.results[0].id
    f = client.folders.get_file(vid, fid, file_id)
    assert f.id == file_id
