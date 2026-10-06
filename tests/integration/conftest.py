from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient
from databrarypy.models import File

pytestmark = pytest.mark.staging

DEFAULT_INTEGRATION_VOLUME_ID = 1777
DEFAULT_INTEGRATION_CATEGORY_ID = 6


def unique_name(prefix: str) -> str:
    """Return a unique name safe for create/rename integration tests."""
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _file_matches_upload_basename(file: File, filename: str) -> bool:
    """Match listed file rows to an upload basename.

    The API exposes ``name`` without the extension (e.g. ``clip``) while
    ``upload.filename`` keeps the original uploaded name (e.g. ``clip.mp4``).
    """
    if file.name == filename:
        return True
    stem = Path(filename).stem
    if file.name == stem:
        return True
    upload = file.upload
    if isinstance(upload, dict):
        upload_name = upload.get("filename")
        if isinstance(upload_name, str) and upload_name == filename:
            return True
    return False


def find_file_by_name(
    client: DatabraryClient,
    volume_id: int,
    container_type: str,
    container_id: int,
    filename: str,
) -> File | None:
    """Find a file by exact basename, scanning all pages via ``files_list``."""
    if container_type == "session":
        iterator = client.sessions.files_list(volume_id, container_id)
    elif container_type == "folder":
        iterator = client.folders.files_list(volume_id, container_id)
    else:
        raise ValueError(f"container_type must be 'session' or 'folder', got {container_type!r}")

    return next((f for f in iterator if _file_matches_upload_basename(f, filename)), None)


@pytest.fixture(scope="session")
def client() -> DatabraryClient:
    env_path = Path(__file__).resolve().parents[2] / ".env"

    client = DatabraryClient.from_env(env_file=env_path, login=True)
    return client


@pytest.fixture(scope="session")
def integration_volume_id() -> int:
    """Volume used for writable integration tests (override via INTEGRATION_VOLUME_ID)."""
    return int(os.environ.get("INTEGRATION_VOLUME_ID", str(DEFAULT_INTEGRATION_VOLUME_ID)))


@pytest.fixture(scope="session")
def integration_category_id() -> int:
    """Record category for integration tests (override via INTEGRATION_CATEGORY_ID)."""
    return int(os.environ.get("INTEGRATION_CATEGORY_ID", str(DEFAULT_INTEGRATION_CATEGORY_ID)))


@pytest.fixture(scope="session")
def writable_volume(
    client: DatabraryClient,
    integration_volume_id: int,
    integration_category_id: int,
) -> int:
    """Probe write access by creating and deleting a ephemeral record."""
    try:
        record = client.records.create(
            integration_volume_id,
            category_id=integration_category_id,
            name=unique_name("writable-probe"),
        )
        client.records.delete(integration_volume_id, record.id)
    except Exception as exc:
        pytest.skip(
            f"Integration volume {integration_volume_id} is not writable "
            f"(category {integration_category_id}): {exc}"
        )
    return integration_volume_id
