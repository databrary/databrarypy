"""FoldersResource tests (list, retrieve, nested files, CRUD)."""

from __future__ import annotations

from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient
from databrarypy.models import FolderDuplicateFileCheckItem
from tests.fixtures.data_constants import TASK_STATUS_PROCESSING, VOLUME_ID_PRIMARY
from tests.fixtures.folders import (
    DUPLICATE_FILENAME,
    FOLDER_FILE_BINARY_CONTENT,
    FOLDER_FILE_ID_1,
    FOLDER_ID_1,
    FOLDER_ID_CREATED,
    JPEG_MIMETYPE,
    _get_mock_folder_1,
    _get_mock_folder_1_files_page,
    _get_mock_folders_page,
    build_composite_transport,
)

MOCK_FOLDERS_PAGE = _get_mock_folders_page()
MOCK_FOLDER_1 = _get_mock_folder_1()
MOCK_FOLDER_1_FILES_PAGE = _get_mock_folder_1_files_page()


def test_folders_list_retrieve_and_files() -> None:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()

    # list
    page = client.folders.page(VOLUME_ID_PRIMARY, page=1, page_size=10)
    assert page.count == 1
    assert page.results and page.results[0].id == FOLDER_ID_1

    # retrieve
    detail = client.folders.retrieve(VOLUME_ID_PRIMARY, FOLDER_ID_1)
    assert detail.id == FOLDER_ID_1
    assert detail.release_level == MOCK_FOLDER_1["release_level"]

    # files list
    files_page = client.folders.files_page(VOLUME_ID_PRIMARY, FOLDER_ID_1)
    assert files_page.count == 1
    f0 = files_page.results[0]
    assert f0.format and f0.format.mimetype == JPEG_MIMETYPE

    # file detail
    fdetail = client.folders.get_file(VOLUME_ID_PRIMARY, FOLDER_ID_1, FOLDER_FILE_ID_1)
    assert fdetail.id == FOLDER_FILE_ID_1
    assert fdetail.folder == FOLDER_ID_1

    # download bytes
    content = client.folders.download_file(VOLUME_ID_PRIMARY, FOLDER_ID_1, FOLDER_FILE_ID_1)
    assert content == FOLDER_FILE_BINARY_CONTENT

    # download to directory: exercises URL-basename fallback since no header
    out_dir = Path(".pytest_tmp/folder_dl")
    saved = client.folders.download_file(
        VOLUME_ID_PRIMARY, FOLDER_ID_1, FOLDER_FILE_ID_1, dest_path=str(out_dir)
    )
    assert saved.startswith(str(out_dir))

    # request folder zip download (task)
    task = client.folders.request_zip_download(VOLUME_ID_PRIMARY, FOLDER_ID_1)
    assert task.status == TASK_STATUS_PROCESSING and task.task_id


def test_folders_iterators() -> None:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()

    first_folder = next(client.folders.list(VOLUME_ID_PRIMARY))
    assert first_folder.id == FOLDER_ID_1
    first_file = next(client.folders.files_list(VOLUME_ID_PRIMARY, FOLDER_ID_1))
    assert first_file.id == FOLDER_FILE_ID_1


def _make_client() -> DatabraryClient:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()
    return client


def test_folders_create() -> None:
    client = _make_client()

    folder = client.folders.create(
        VOLUME_ID_PRIMARY,
        name="My New Folder",
        release_level="private",
        source_date="2026-01-15",
    )
    assert folder.id == FOLDER_ID_CREATED
    assert folder.name == "My New Folder"
    assert folder.release_level == "private"
    assert folder.source_date == "2026-01-15"


def test_folders_create_minimal() -> None:
    client = _make_client()

    folder = client.folders.create(VOLUME_ID_PRIMARY, name="Minimal")
    assert folder.id == FOLDER_ID_CREATED
    assert folder.name == "Minimal"


def test_folders_create_rejects_blank_name() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="non-empty"):
        client.folders.create(VOLUME_ID_PRIMARY, name="   ")


def test_folders_update_put() -> None:
    client = _make_client()

    folder = client.folders.update(
        VOLUME_ID_PRIMARY,
        FOLDER_ID_1,
        name="Renamed",
        release_level="public",
        source_date="2026-02-01",
    )
    assert folder.id == FOLDER_ID_1
    assert folder.name == "Renamed"
    assert folder.source_date == "2026-02-01"


def test_folders_update_put_name_only() -> None:
    client = _make_client()

    folder = client.folders.update(VOLUME_ID_PRIMARY, FOLDER_ID_1, name="Renamed in place")
    assert folder.id == FOLDER_ID_1
    assert folder.name == "Renamed in place"
    assert folder.release_level == _get_mock_folder_1()["release_level"]


def test_folders_patch_name_only() -> None:
    client = _make_client()

    folder = client.folders.patch(VOLUME_ID_PRIMARY, FOLDER_ID_1, name="Just renamed")
    assert folder.id == FOLDER_ID_1
    assert folder.name == "Just renamed"
    # Other fields preserved from base mock folder
    assert folder.release_level == _get_mock_folder_1()["release_level"]


def test_folders_patch_rejects_blank_name() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="non-empty"):
        client.folders.patch(VOLUME_ID_PRIMARY, FOLDER_ID_1, name="  \t")


def test_folders_patch_requires_fields() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="At least one"):
        client.folders.patch(VOLUME_ID_PRIMARY, FOLDER_ID_1)


def test_folders_delete() -> None:
    client = _make_client()

    assert client.folders.delete(VOLUME_ID_PRIMARY, FOLDER_ID_1) is True


def test_folders_check_duplicate_files() -> None:
    client = _make_client()

    result = client.folders.check_duplicate_files(
        VOLUME_ID_PRIMARY,
        FOLDER_ID_1,
        filenames=[DUPLICATE_FILENAME, "new_file.jpg"],
    )
    assert result == [
        FolderDuplicateFileCheckItem(filename=DUPLICATE_FILENAME, exists=True),
        FolderDuplicateFileCheckItem(filename="new_file.jpg", exists=False),
    ]


def test_folders_check_duplicate_files_empty() -> None:
    client = _make_client()

    result = client.folders.check_duplicate_files(VOLUME_ID_PRIMARY, FOLDER_ID_1, filenames=[])
    assert result == []


# ------------------------------------------------------------------
# File metadata (update_file / patch_file / delete_file)
# ------------------------------------------------------------------


def test_folders_update_file_put() -> None:
    client = _make_client()

    file_obj = client.folders.update_file(
        VOLUME_ID_PRIMARY,
        FOLDER_ID_1,
        FOLDER_FILE_ID_1,
        name="Renamed Image",
        release_level="private",
    )
    assert file_obj.id == FOLDER_FILE_ID_1
    assert file_obj.name == "Renamed Image"
    assert file_obj.release_level == "private"


def test_folders_patch_file_name_only() -> None:
    client = _make_client()

    file_obj = client.folders.patch_file(
        VOLUME_ID_PRIMARY,
        FOLDER_ID_1,
        FOLDER_FILE_ID_1,
        name="Just Renamed",
    )
    assert file_obj.name == "Just Renamed"


def test_folders_patch_file_requires_fields() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="At least one"):
        client.folders.patch_file(VOLUME_ID_PRIMARY, FOLDER_ID_1, FOLDER_FILE_ID_1)


def test_folders_delete_file() -> None:
    client = _make_client()

    assert client.folders.delete_file(VOLUME_ID_PRIMARY, FOLDER_ID_1, FOLDER_FILE_ID_1) is True
