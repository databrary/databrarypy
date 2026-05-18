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
JPEG_MIMETYPE = "image/jpeg"
FOLDER_FILE_BINARY_CONTENT = b"FOLDER_FILE_CONTENT"
FOLDER_FILE_DEFAULT_NAME = "Image 1.jpg"


def _get_mock_folder_1():
    return {
        "id": FOLDER_ID_1,
        "name": "Folder A",
        "volume": VOLUME_ID_PRIMARY,
        "release_level": "public",
        "created_at": "2025-06-02T10:00:00Z",
        "updated_at": "2025-06-02T10:10:00Z",
        "source_date": "2025-06-01",
        "file_counts": {"native_total": 1, "linked_total": 0},
        "has_full_access": True,
        "contains_different_release_levels": False,
        "source_info": None,
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
            "mimetype": JPEG_MIMETYPE,
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
        "mime_type": JPEG_MIMETYPE,
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


# ---- Downloads ----
def handle_folder_file_download_link(request: httpx.Request) -> httpx.Response:
    # Signed link payload for folder file download
    payload = {
        "download_url": "/dl/folder-file.bin?token=abc",
        "expires_at": "2030-01-01T00:00:00Z",
        "file_name": FOLDER_FILE_DEFAULT_NAME,
        "file_size": 654321,
    }
    return httpx.Response(200, json=payload)


def handle_folder_file_binary(request: httpx.Request) -> httpx.Response:
    # No content-disposition header on purpose to exercise URL basename fallback
    return httpx.Response(200, content=FOLDER_FILE_BINARY_CONTENT)


def handle_folder_zip_download_link(request: httpx.Request) -> httpx.Response:
    # Folder-level zip generation task
    return httpx.Response(
        200, json={"status": "processing", "message": None, "task_id": "zip-folder-1"}
    )


# ---- Write handlers (CRUD) ----
FOLDER_ID_CREATED = 302
DUPLICATE_FILENAME = "existing.jpg"


def _folder_response_with(
    name: str = "Folder A", release_level: str = "public", source_date: str | None = "2025-06-01"
) -> dict:
    folder = _get_mock_folder_1()
    folder["name"] = name
    folder["release_level"] = release_level
    folder["source_date"] = source_date
    return folder


def handle_folder_create(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    response = _folder_response_with(
        name=body.get("name", "Folder A"),
        release_level=body.get("release_level", "public"),
        source_date=body.get("source_date"),
    )
    response["id"] = FOLDER_ID_CREATED
    return httpx.Response(201, json=response)


def handle_folder_put(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    base = dict(_get_mock_folder_1())
    if "name" in body:
        base["name"] = body["name"]
    if "release_level" in body:
        base["release_level"] = body["release_level"]
    if "source_date" in body:
        base["source_date"] = body["source_date"]
    return httpx.Response(200, json=base)


def handle_folder_patch(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    base = _get_mock_folder_1()
    if "name" in body:
        base["name"] = body["name"]
    if "release_level" in body:
        base["release_level"] = body["release_level"]
    if "source_date" in body:
        base["source_date"] = body["source_date"]
    return httpx.Response(200, json=base)


def handle_folder_delete(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def handle_check_duplicate_files(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    filenames = body.get("filenames", [])
    result = [{"filename": fn, "exists": fn == DUPLICATE_FILENAME} for fn in filenames]
    return httpx.Response(200, json=result)


# ---- File metadata handlers ----
def _folder_file_response_with(**overrides) -> dict:
    base = _get_mock_folder_1_file()
    base.update(overrides)
    return base


def handle_folder_file_put(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    return httpx.Response(
        200,
        json=_folder_file_response_with(
            name=body.get("name") or "Image 1.jpg",
            release_level=body.get("release_level") or "public",
        ),
    )


def handle_folder_file_patch(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    overrides = {k: v for k, v in body.items() if k in {"name", "release_level"}}
    return httpx.Response(200, json=_folder_file_response_with(**overrides))


def handle_folder_file_delete(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def build_folders_transport():
    return build_transport(
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/folders/", handle_folders_list),
        ("POST", f"/volumes/{VOLUME_ID_PRIMARY}/folders/", handle_folder_create),
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/", handle_folder_detail),
        ("PUT", f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/", handle_folder_put),
        ("PATCH", f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/", handle_folder_patch),
        ("DELETE", f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/", handle_folder_delete),
        (
            "POST",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/check-duplicate-files/",
            handle_check_duplicate_files,
        ),
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
        (
            "PUT",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/files/{FOLDER_FILE_ID_1}/",
            handle_folder_file_put,
        ),
        (
            "PATCH",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/files/{FOLDER_FILE_ID_1}/",
            handle_folder_file_patch,
        ),
        (
            "DELETE",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/files/{FOLDER_FILE_ID_1}/",
            handle_folder_file_delete,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/files/{FOLDER_FILE_ID_1}/download-link/",
            handle_folder_file_download_link,
        ),
        ("GET", "/dl/folder-file.bin", handle_folder_file_binary),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/folders/{FOLDER_ID_1}/download-link/",
            handle_folder_zip_download_link,
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
