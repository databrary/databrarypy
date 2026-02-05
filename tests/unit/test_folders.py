"""FoldersResource tests (list, retrieve, nested files)."""

from __future__ import annotations

from pathlib import Path

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import TASK_STATUS_PROCESSING, VOLUME_ID_PRIMARY
from tests.fixtures.folders import (
    FOLDER_FILE_BINARY_CONTENT,
    FOLDER_FILE_ID_1,
    FOLDER_ID_1,
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
        user_agent="dbpy-tests",
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
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    first_folder = next(client.folders.list(VOLUME_ID_PRIMARY))
    assert first_folder.id == FOLDER_ID_1
    first_file = next(client.folders.files_list(VOLUME_ID_PRIMARY, FOLDER_ID_1))
    assert first_file.id == FOLDER_FILE_ID_1
