from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def _first_volume_id(client: DatabraryClient) -> int | None:
    vols = client.volumes.list(page=1)
    return _first_id(vols)


def test_folders_list_and_retrieve(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.folders.list(vid, page=1)
    assert page.count >= 0
    fid = _first_id(page)
    if fid is not None:
        folder = client.folders.retrieve(vid, fid)
        assert folder.id == fid


def test_folders_files_and_downloads(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.folders.list(vid, page=1)
    if not page.results:
        return
    fid = page.results[0].id

    files = client.folders.files(vid, fid, page=1)
    assert files.count >= 0
