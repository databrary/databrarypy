from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from tests.integration.conftest import find_file_by_name, unique_name

from databrarypy.client import DatabraryClient
from databrarypy.models.bulk import BulkItemStatus
from databrarypy.models.uploads import UploadStatus


def _delete_uploaded_file(
    client: DatabraryClient,
    volume_id: int,
    destination_type: str,
    object_id: int,
    filename: str,
) -> None:
    """Best-effort cleanup of an uploaded file by basename."""
    with suppress(Exception):
        uploaded = find_file_by_name(client, volume_id, destination_type, object_id, filename)
        if uploaded is None:
            return
        if destination_type == "session":
            client.sessions.delete_file(volume_id, object_id, uploaded.id)
        else:
            client.folders.delete_file(volume_id, object_id, uploaded.id)


def test_upload_file_to_session(
    client: DatabraryClient,
    writable_volume: int,
    tmp_path: Path,
):
    session = client.sessions.create(writable_volume, name=unique_name("upload-session"))
    filename = f"{unique_name('upload')}.txt"
    file_path = tmp_path / filename
    file_path.write_bytes(b"integration upload content\n")

    try:
        result = client.uploads.upload_file(
            file_path,
            destination_type="session",
            object_id=session.id,
            poll_interval=2.0,
            poll_timeout=120.0,
        )
        assert result.upload_type == "single"
        assert result.final_status == UploadStatus.COMPLETED.value
        assert result.status_url
    finally:
        _delete_uploaded_file(client, writable_volume, "session", session.id, filename)
        client.sessions.delete(writable_volume, session.id)


def test_upload_file_to_folder(
    client: DatabraryClient,
    writable_volume: int,
    tmp_path: Path,
):
    folder = client.folders.create(writable_volume, name=unique_name("upload-folder"))
    filename = f"{unique_name('upload')}.txt"
    file_path = tmp_path / filename
    file_path.write_bytes(b"integration folder upload\n")

    try:
        result = client.uploads.upload_file(
            file_path,
            destination_type="folder",
            object_id=folder.id,
            poll_interval=2.0,
            poll_timeout=120.0,
        )
        assert result.upload_type == "single"
        assert result.final_status == UploadStatus.COMPLETED.value
        assert result.status_url
    finally:
        _delete_uploaded_file(client, writable_volume, "folder", folder.id, filename)
        client.folders.delete(writable_volume, folder.id)


def test_bulk_upload_files_with_duplicate_preflight(
    client: DatabraryClient,
    writable_volume: int,
    tmp_path: Path,
):
    session = client.sessions.create(writable_volume, name=unique_name("bulk-upload-session"))
    filename = f"{unique_name('bulk')}.txt"
    file_path = tmp_path / filename
    file_path.write_bytes(b"bulk upload one\n")

    try:
        first = client.uploads.upload_file(
            file_path,
            destination_type="session",
            object_id=session.id,
            poll_interval=2.0,
            poll_timeout=120.0,
        )
        assert first.final_status == UploadStatus.COMPLETED.value

        bulk = client.uploads.bulk_upload_files(
            [file_path],
            destination_type="session",
            object_id=session.id,
            volume_id=writable_volume,
            preflight=True,
            poll_interval=2.0,
            poll_timeout=120.0,
        )
        assert len(bulk.skipped) == 1
        assert bulk.skipped[0].reason == "duplicate"
        assert bulk.skipped[0].status == BulkItemStatus.SKIPPED
    finally:
        _delete_uploaded_file(client, writable_volume, "session", session.id, filename)
        client.sessions.delete(writable_volume, session.id)
