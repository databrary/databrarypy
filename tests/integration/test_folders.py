from __future__ import annotations

from pathlib import Path

import pytest
from tests.conftest import collect_items, first_page_item
from tests.integration.conftest import find_file_by_name, unique_name

from databrarypy.client import DatabraryClient
from databrarypy.models.uploads import UploadStatus


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


def test_folders_crud_lifecycle(client: DatabraryClient, writable_volume: int):
    """Create -> retrieve -> update -> patch -> delete."""
    name = unique_name("integ-folder")
    folder = client.folders.create(writable_volume, name=name)
    assert folder.id > 0
    assert folder.name == name

    try:
        retrieved = client.folders.retrieve(writable_volume, folder.id)
        assert retrieved.id == folder.id

        updated = client.folders.update(
            writable_volume,
            folder.id,
            name=unique_name("integ-folder-upd"),
        )
        assert updated.id == folder.id

        patched = client.folders.patch(
            writable_volume,
            folder.id,
            name=unique_name("integ-folder-patch"),
        )
        assert patched.id == folder.id
    finally:
        assert client.folders.delete(writable_volume, folder.id) is True


def test_folders_check_duplicate_files(client: DatabraryClient, writable_volume: int):
    name = unique_name("integ-folder-dup")
    folder = client.folders.create(writable_volume, name=name)
    try:
        result = client.folders.check_duplicate_files(
            writable_volume,
            folder.id,
            filenames=["nonexistent-file-xyz.txt", "another-new-file.bin"],
        )
        assert len(result) == 2
        assert all(not item.exists for item in result)
    finally:
        client.folders.delete(writable_volume, folder.id)


def test_folders_download_file_and_zip(
    client: DatabraryClient,
    writable_volume: int,
    tmp_path: Path,
):
    """Upload a file into an ephemeral folder, then download it and request ZIP."""
    folder = client.folders.create(writable_volume, name=unique_name("dl-folder"))
    filename = f"{unique_name('dl')}.txt"
    file_path = tmp_path / filename
    file_path.write_bytes(b"download integration test\n")

    try:
        upload = client.uploads.upload_file(
            file_path,
            destination_type="folder",
            object_id=folder.id,
            poll_interval=2.0,
            poll_timeout=120.0,
        )
        assert upload.final_status == UploadStatus.COMPLETED.value

        uploaded = find_file_by_name(client, writable_volume, "folder", folder.id, filename)
        assert uploaded is not None, f"Uploaded file {filename!r} not found in folder file list"

        content = client.folders.download_file(writable_volume, folder.id, uploaded.id)
        assert isinstance(content, bytes)
        assert len(content) > 0

        dest_dir = tmp_path / "folder-dl"
        dest_dir.mkdir()
        saved = client.folders.download_file(
            writable_volume,
            folder.id,
            uploaded.id,
            dest_path=str(dest_dir),
        )
        assert Path(saved).is_file()

        task = client.folders.request_zip_download(writable_volume, folder.id)
        assert task.task_id
    finally:
        client.folders.delete(writable_volume, folder.id)
