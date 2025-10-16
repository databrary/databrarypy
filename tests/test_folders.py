"""FoldersResource tests (list, retrieve, nested files)."""

from __future__ import annotations

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import VOLUME_ID_PRIMARY
from tests.fixtures.folders import (
    FOLDER_FILE_ID_1,
    FOLDER_ID_1,
    JPEG_MIMETYPE,
    build_composite_transport,
)


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
    page = client.folders.list(VOLUME_ID_PRIMARY, page=1, page_size=10)
    assert page.count == 1
    assert page.results and page.results[0].id == FOLDER_ID_1

    # retrieve
    detail = client.folders.retrieve(VOLUME_ID_PRIMARY, FOLDER_ID_1)
    assert detail.id == FOLDER_ID_1
    assert detail.release_level == "public"

    # files list
    files_page = client.folders.files(VOLUME_ID_PRIMARY, FOLDER_ID_1)
    assert files_page.count == 1
    f0 = files_page.results[0]
    assert f0.format and f0.format.mimetype == JPEG_MIMETYPE

    # file detail
    fdetail = client.folders.get_file(VOLUME_ID_PRIMARY, FOLDER_ID_1, FOLDER_FILE_ID_1)
    assert fdetail.id == FOLDER_FILE_ID_1
    assert fdetail.folder == FOLDER_ID_1
