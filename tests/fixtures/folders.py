"""Folders fixtures and mock handlers (including nested files)."""

from __future__ import annotations

import httpx

from .client import build_client_transport
from .common import build_transport
from .data_constants import VOLUME_ID_PRIMARY
from .factory import make_page

# ---- IDs ----
FOLDER_ID_1 = 301
FOLDER_FILE_ID_1 = 3001


def _get_mock_folder_1():
    return {
        "id": FOLDER_ID_1,
        "name": "Folder A",
        "volume": VOLUME_ID_PRIMARY,
        "release_level": "public",
        "created_at": "2025-06-02T10:00:00Z",
        "updated_at": "2025-06-02T10:10:00Z",
        "source_date": "2025-06-01",
        "file_count": 1,
        "accessible_file_count": 1,
        "has_full_access": True,
        "contains_different_release_levels": False,
    }


def _get_mock_folder_1_file():
    return {
        "id": FOLDER_FILE_ID_1,
        "name": "Image 1.jpg",
        "uploader": {"id": 6, "first_name": "Alex", "last_name": "Doe"},
        "created_at": "2025-06-02T10:02:00Z",
        "updated_at": "2025-06-02T10:03:00Z",
        "upload": {"status": "completed"},
        "records": [],
        "release_level": "public",
        "format": {
            "id": 10,
            "mimetype": "image/jpeg",
            "name": "JPEG",
            "extensions": [".jpg", ".jpeg"],
        },
        "source_date": "2025-06-01",
        "date": {"year": 2025, "month": 6, "day": 1},
        "sha1": "def456",
        "size": 654321,
        "volume": VOLUME_ID_PRIMARY,
        "folder": FOLDER_ID_1,
        "session": None,
        "mime_type": "image/jpeg",
        "transcoded_file": None,
        "has_full_access": True,
        "thumbnail_url": "https://cdn.example/thumb2.jpg",
    }


# ---- Paged payloads ----
def _get_mock_folders_page():
    return make_page(results=[_get_mock_folder_1()], count=1)


def _get_mock_folder_1_files_page():
    return make_page(results=[_get_mock_folder_1_file()], count=1)


# ---- Handlers ----
def handle_folders_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_folders_page())


def handle_folder_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_folder_1())


def handle_folder_files_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_folder_1_files_page())


def handle_folder_file_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_folder_1_file())


def build_folders_transport():
    return build_transport(
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/folders/", handle_folders_list),
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/", handle_folder_detail),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/files/",
            handle_folder_files_list,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/files/{FOLDER_FILE_ID_1}/",
            handle_folder_file_detail,
        ),
    )


def build_composite_transport():
    client_transport = build_client_transport()
    folders_transport = build_folders_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return folders_transport.handle_request(request)

    return httpx.MockTransport(router)
