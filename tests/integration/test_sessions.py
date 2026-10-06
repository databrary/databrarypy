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


def test_sessions_crud_lifecycle(client: DatabraryClient, writable_volume: int):
    """Create -> retrieve -> update -> patch -> delete."""
    name = unique_name("integ-session")
    session = client.sessions.create(writable_volume, name=name)
    assert session.id > 0
    assert session.name == name

    try:
        retrieved = client.sessions.retrieve(writable_volume, session.id)
        assert retrieved.id == session.id

        updated = client.sessions.update(
            writable_volume,
            session.id,
            name=unique_name("integ-session-upd"),
        )
        assert updated.id == session.id

        patched = client.sessions.patch(
            writable_volume,
            session.id,
            name=unique_name("integ-session-patch"),
        )
        assert patched.id == session.id
    finally:
        assert client.sessions.delete(writable_volume, session.id) is True


def test_sessions_check_duplicate_files(client: DatabraryClient, writable_volume: int):
    name = unique_name("integ-session-dup")
    session = client.sessions.create(writable_volume, name=name)
    try:
        result = client.sessions.check_duplicate_files(
            writable_volume,
            session.id,
            filenames=["nonexistent-file-xyz.txt"],
        )
        assert len(result) == 1
        assert result[0].exists is False
    finally:
        client.sessions.delete(writable_volume, session.id)


def test_sessions_csv_and_zip_tasks(client: DatabraryClient, writable_volume: int):
    page = client.sessions.page(writable_volume, page=1)
    next_session = first_page_item(page)
    if next_session is None:
        pytest.skip("No sessions available for export task test")
    sid = next_session.id

    zip_task = client.sessions.request_zip_download(writable_volume, sid)
    assert zip_task.task_id

    csv_task = client.sessions.request_csv_download(writable_volume, sid)
    assert csv_task.task_id


def test_sessions_assign_record_to_file(
    client: DatabraryClient,
    writable_volume: int,
    integration_category_id: int,
):
    page = client.sessions.page(writable_volume, page=1)
    next_session = first_page_item(page)
    if next_session is None:
        pytest.skip("No sessions available for assign test")
    sid = next_session.id
    files = client.sessions.files_page(writable_volume, sid, page=1)
    next_file = first_page_item(files)
    if next_file is None:
        pytest.skip("No session files available for assign test")

    record = client.records.create(
        writable_volume,
        category_id=integration_category_id,
        name=unique_name("assign-record"),
    )
    try:
        client.sessions.assign_record_to_file(
            writable_volume,
            sid,
            next_file.id,
            record.id,
        )
        client.sessions.assign_record_to_file(
            writable_volume,
            sid,
            next_file.id,
            record.id,
        )
        client.sessions.unassign_record_from_file(
            writable_volume,
            sid,
            next_file.id,
            record.id,
        )
    finally:
        client.records.delete(writable_volume, record.id)


def test_sessions_download_file(
    client: DatabraryClient,
    writable_volume: int,
    tmp_path: Path,
):
    """Upload a file into an ephemeral session, then download it."""
    session = client.sessions.create(writable_volume, name=unique_name("dl-session"))
    filename = f"{unique_name('dl')}.txt"
    file_path = tmp_path / filename
    file_path.write_bytes(b"session download integration test\n")

    try:
        upload = client.uploads.upload_file(
            file_path,
            destination_type="session",
            object_id=session.id,
            poll_interval=2.0,
            poll_timeout=120.0,
        )
        assert upload.final_status == UploadStatus.COMPLETED.value

        uploaded = find_file_by_name(client, writable_volume, "session", session.id, filename)
        assert uploaded is not None, f"Uploaded file {filename!r} not found in session file list"

        content = client.sessions.download_file(writable_volume, session.id, uploaded.id)
        assert isinstance(content, bytes)
        assert len(content) > 0

        dest_dir = tmp_path / "session-dl"
        dest_dir.mkdir()
        saved = client.sessions.download_file(
            writable_volume,
            session.id,
            uploaded.id,
            dest_path=str(dest_dir),
        )
        assert Path(saved).is_file()
    finally:
        client.sessions.delete(writable_volume, session.id)
