from __future__ import annotations

from contextlib import suppress

from tests.integration.conftest import unique_name

from databrarypy.client import DatabraryClient
from databrarypy.models.bulk import BulkItemStatus


def test_folders_bulk_create_rename_delete(client: DatabraryClient, writable_volume: int):
    names = [unique_name("bulk-folder-a"), unique_name("bulk-folder-b")]
    folder_ids: list[int] = []

    try:
        bulk_create = client.folders.bulk_create(
            writable_volume,
            [{"name": n} for n in names],
        )
        assert len(bulk_create.succeeded) == 2
        folder_ids = [item.result.id for item in bulk_create.succeeded]

        bulk_rename = client.folders.bulk_rename(
            writable_volume,
            [(folder_ids[0], unique_name("bulk-folder-renamed"))],
        )
        assert len(bulk_rename.succeeded) == 1

        bulk_delete = client.folders.bulk_delete(writable_volume, folder_ids)
        assert len(bulk_delete.succeeded) == 2
        assert all(item.status == BulkItemStatus.SUCCESS for item in bulk_delete.items)
        folder_ids = []
    finally:
        for fid in folder_ids:
            with suppress(Exception):
                client.folders.delete(writable_volume, fid)


def test_sessions_bulk_create_delete(client: DatabraryClient, writable_volume: int):
    names = [unique_name("bulk-session-a"), unique_name("bulk-session-b")]
    session_ids: list[int] = []

    try:
        bulk_create = client.sessions.bulk_create(
            writable_volume,
            [{"name": n} for n in names],
        )
        assert len(bulk_create.succeeded) == 2
        session_ids = [item.result.id for item in bulk_create.succeeded]

        bulk_delete = client.sessions.bulk_delete(writable_volume, session_ids)
        assert len(bulk_delete.succeeded) == 2
        session_ids = []
    finally:
        for sid in session_ids:
            with suppress(Exception):
                client.sessions.delete(writable_volume, sid)
