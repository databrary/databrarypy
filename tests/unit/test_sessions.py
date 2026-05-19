"""SessionsResource tests (list, retrieve, nested files, CRUD)."""

from __future__ import annotations

from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient
from databrarypy.models import SessionDuplicateFileCheckItem
from tests.fixtures.data_constants import TASK_STATUS_PROCESSING, VOLUME_ID_PRIMARY
from tests.fixtures.sessions import (
    DEFAULT_RECORD_ID,
    SESSION_DUPLICATE_FILENAME,
    SESSION_FILE_BINARY_CONTENT,
    SESSION_FILE_DEFAULT_NAME,
    SESSION_FILE_ID_1,
    SESSION_ID_1,
    SESSION_ID_CREATED,
    _get_mock_session_1,
    _get_mock_session_1_file,
    _get_mock_session_1_files_page,
    _get_mock_sessions_page,
    build_composite_transport,
)

MOCK_SESSIONS_PAGE = _get_mock_sessions_page()
MOCK_SESSION_1 = _get_mock_session_1()
MOCK_SESSION_1_FILES_PAGE = _get_mock_session_1_files_page()
MOCK_SESSION_1_FILE = _get_mock_session_1_file()


def test_sessions_list_retrieve_and_files() -> None:
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
    page = client.sessions.page(VOLUME_ID_PRIMARY, page=1, page_size=10)
    assert page.count == 1
    assert page.results and page.results[0].id == SESSION_ID_1

    # retrieve
    detail = client.sessions.retrieve(VOLUME_ID_PRIMARY, SESSION_ID_1)
    assert detail.id == SESSION_ID_1
    assert detail.release_level == MOCK_SESSION_1["release_level"]

    # files list
    files_page = client.sessions.files_page(VOLUME_ID_PRIMARY, SESSION_ID_1)
    assert files_page.count == 1
    f0 = files_page.results[0]
    assert f0.format and f0.format.mimetype.startswith("video/")

    # file detail
    fdetail = client.sessions.get_file(VOLUME_ID_PRIMARY, SESSION_ID_1, SESSION_FILE_ID_1)
    assert fdetail.id == SESSION_FILE_ID_1
    tf = fdetail.transcoded_file
    assert tf.id == MOCK_SESSION_1_FILE["transcoded_file"]["id"]

    # download bytes
    content = client.sessions.download_file(VOLUME_ID_PRIMARY, SESSION_ID_1, SESSION_FILE_ID_1)
    assert content == SESSION_FILE_BINARY_CONTENT

    # download to dir should use header-provided filename
    out_dir = Path(".pytest_tmp/session_dl")
    if out_dir.exists() and out_dir.is_file():
        out_dir.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = client.sessions.download_file(
        VOLUME_ID_PRIMARY, SESSION_ID_1, SESSION_FILE_ID_1, dest_path=str(out_dir)
    )
    assert saved.endswith(SESSION_FILE_DEFAULT_NAME)

    # request session tasks (zip, csv)
    zip_task = client.sessions.request_zip_download(VOLUME_ID_PRIMARY, SESSION_ID_1)
    assert zip_task.status == TASK_STATUS_PROCESSING
    csv_task = client.sessions.request_csv_download(VOLUME_ID_PRIMARY, SESSION_ID_1)
    assert csv_task.status == TASK_STATUS_PROCESSING


def test_sessions_iterators() -> None:
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

    first_session = next(client.sessions.list(VOLUME_ID_PRIMARY))
    assert first_session.id == SESSION_ID_1
    first_sfile = next(client.sessions.files_list(VOLUME_ID_PRIMARY, SESSION_ID_1))
    assert first_sfile.id is not None


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


# ------------------------------------------------------------------
# Create
# ------------------------------------------------------------------


def test_sessions_create() -> None:
    client = _make_client()

    session = client.sessions.create(
        VOLUME_ID_PRIMARY,
        name="New Session",
        release_level="private",
        source_date="2026-03-01",
    )
    assert session.id == SESSION_ID_CREATED
    assert session.name == "New Session"
    assert session.release_level == "private"
    assert session.source_date == "2026-03-01"


def test_sessions_create_minimal() -> None:
    client = _make_client()

    session = client.sessions.create(VOLUME_ID_PRIMARY, name="Minimal")
    assert session.id == SESSION_ID_CREATED
    assert session.name == "Minimal"


def test_sessions_create_rejects_blank_name() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="non-empty"):
        client.sessions.create(VOLUME_ID_PRIMARY, name="   ")


# ------------------------------------------------------------------
# Update (PUT)
# ------------------------------------------------------------------


def test_sessions_update_put() -> None:
    client = _make_client()

    session = client.sessions.update(
        VOLUME_ID_PRIMARY,
        SESSION_ID_1,
        name="Renamed Session",
        release_level="public",
        source_date="2026-04-01",
    )
    assert session.id == SESSION_ID_1
    assert session.name == "Renamed Session"
    assert session.source_date == "2026-04-01"


def test_sessions_update_put_name_only() -> None:
    client = _make_client()

    session = client.sessions.update(VOLUME_ID_PRIMARY, SESSION_ID_1, name="Renamed in place")
    assert session.id == SESSION_ID_1
    assert session.name == "Renamed in place"
    assert session.release_level == _get_mock_session_1()["release_level"]


def test_sessions_update_rejects_blank_name() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="non-empty"):
        client.sessions.update(VOLUME_ID_PRIMARY, SESSION_ID_1, name="  \n")


# ------------------------------------------------------------------
# Patch (partial)
# ------------------------------------------------------------------


def test_sessions_patch_name_only() -> None:
    client = _make_client()

    session = client.sessions.patch(VOLUME_ID_PRIMARY, SESSION_ID_1, name="Patched")
    assert session.id == SESSION_ID_1
    assert session.name == "Patched"
    assert session.release_level == _get_mock_session_1()["release_level"]


def test_sessions_patch_requires_fields() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="At least one"):
        client.sessions.patch(VOLUME_ID_PRIMARY, SESSION_ID_1)


def test_sessions_patch_rejects_blank_name() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="non-empty"):
        client.sessions.patch(VOLUME_ID_PRIMARY, SESSION_ID_1, name="  \t")


# ------------------------------------------------------------------
# Delete
# ------------------------------------------------------------------


def test_sessions_delete() -> None:
    client = _make_client()

    assert client.sessions.delete(VOLUME_ID_PRIMARY, SESSION_ID_1) is True


# ------------------------------------------------------------------
# Default records
# ------------------------------------------------------------------


def test_sessions_add_default_record() -> None:
    client = _make_client()

    assert (
        client.sessions.add_default_record(VOLUME_ID_PRIMARY, SESSION_ID_1, DEFAULT_RECORD_ID)
        is True
    )


def test_sessions_remove_default_record() -> None:
    client = _make_client()

    assert (
        client.sessions.remove_default_record(VOLUME_ID_PRIMARY, SESSION_ID_1, DEFAULT_RECORD_ID)
        is True
    )


# ------------------------------------------------------------------
# Check duplicate files
# ------------------------------------------------------------------


def test_sessions_check_duplicate_files() -> None:
    client = _make_client()

    result = client.sessions.check_duplicate_files(
        VOLUME_ID_PRIMARY,
        SESSION_ID_1,
        filenames=[SESSION_DUPLICATE_FILENAME, "new_video.mp4"],
    )
    assert result == [
        SessionDuplicateFileCheckItem(filename=SESSION_DUPLICATE_FILENAME, exists=True),
        SessionDuplicateFileCheckItem(filename="new_video.mp4", exists=False),
    ]


def test_sessions_check_duplicate_files_empty() -> None:
    client = _make_client()

    result = client.sessions.check_duplicate_files(VOLUME_ID_PRIMARY, SESSION_ID_1, filenames=[])
    assert result == []


# ------------------------------------------------------------------
# File metadata (update_file / patch_file / delete_file)
# ------------------------------------------------------------------


def test_sessions_update_file_put() -> None:
    client = _make_client()

    file_obj = client.sessions.update_file(
        VOLUME_ID_PRIMARY,
        SESSION_ID_1,
        SESSION_FILE_ID_1,
        name="Renamed Video",
        release_level="private",
        source_date="2026-05-01",
    )
    assert file_obj.id == SESSION_FILE_ID_1
    assert file_obj.name == "Renamed Video"
    assert file_obj.release_level == "private"
    assert file_obj.source_date == "2026-05-01"


def test_sessions_patch_file_name_only() -> None:
    client = _make_client()

    file_obj = client.sessions.patch_file(
        VOLUME_ID_PRIMARY,
        SESSION_ID_1,
        SESSION_FILE_ID_1,
        name="Patched Name",
    )
    assert file_obj.name == "Patched Name"


def test_sessions_patch_file_requires_fields() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="At least one"):
        client.sessions.patch_file(VOLUME_ID_PRIMARY, SESSION_ID_1, SESSION_FILE_ID_1)


def test_sessions_delete_file() -> None:
    client = _make_client()

    assert client.sessions.delete_file(VOLUME_ID_PRIMARY, SESSION_ID_1, SESSION_FILE_ID_1) is True


def test_sessions_check_duplicate_files_rejects_non_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _make_client()

    monkeypatch.setattr(client.sessions, "_post_json", lambda *args, **kwargs: {})

    with pytest.raises(ValueError, match="expected a JSON array"):
        client.sessions.check_duplicate_files(VOLUME_ID_PRIMARY, SESSION_ID_1, filenames=["a.mp4"])
