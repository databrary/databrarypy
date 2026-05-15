"""Sessions fixtures and mock handlers (including nested files)."""

from __future__ import annotations

import httpx

from .client import build_client_transport
from .common import build_transport
from .data_constants import TASK_STATUS_PROCESSING, VOLUME_ID_PRIMARY
from .factory import make_page

# ---- IDs ----
SESSION_ID_1 = 101
SESSION_FILE_ID_1 = 1001


def _get_mock_session_1():
    return {
        "id": SESSION_ID_1,
        "name": "Session A",
        "volume": VOLUME_ID_PRIMARY,
        "release_level": "public",
        "created_at": "2025-06-01T12:00:00Z",
        "updated_at": "2025-06-01T12:30:00Z",
        "source_date": "2025-05-31",
        "date": {"year": 2025, "month": 5, "day": 31},
        "default_records": [],
        "file_records": [],
        "file_counts": {"native_total": 1, "linked_total": 0},
        "has_full_access": True,
        "contains_different_release_levels": False,
        "source_info": None,
    }


def _get_mock_session_1_file():
    return {
        "id": SESSION_FILE_ID_1,
        "name": "Video 1.mp4",
        "uploader": {"id": 6, "first_name": "Alex", "last_name": "Doe"},
        "created_at": "2025-06-01T12:05:00Z",
        "updated_at": "2025-06-01T12:06:00Z",
        "upload": {"status": "completed"},
        "records": [],
        "release_level": "public",
        # Parsed into Format model by pydantic
        "format": {
            "id": 1,
            "mimetype": "video/mp4",
            "name": "MP4",
            "extensions": [".mp4"],
        },
        "source_date": "2025-05-31",
        "date": {"year": 2025, "month": 5, "day": 31},
        "sha1": "abc123",
        "size": 123456,
        "volume": VOLUME_ID_PRIMARY,
        "folder": None,
        "session": SESSION_ID_1,
        "mime_type": "video/mp4",
        "transcoded_file": {
            "id": 2001,
            "name": "Video 1 (HLS)",
            "format": {"name": "HLS", "mimetype": "application/vnd.apple.mpegurl"},
            "sha1": None,
        },
        "has_full_access": True,
        "thumbnail_url": "https://cdn.example/thumb.jpg",
    }


# ---- Paged payloads ----
def _get_mock_sessions_page():
    return make_page(results=[_get_mock_session_1()], count=1)


def _get_mock_session_1_files_page():
    return make_page(results=[_get_mock_session_1_file()], count=1)


# ---- Handlers ----
def handle_sessions_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_sessions_page())


def handle_session_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_session_1())


def handle_session_files_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_session_1_files_page())


def handle_session_file_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_session_1_file())


# ---- Downloads ----
def handle_session_file_download_link(request: httpx.Request) -> httpx.Response:
    payload = {
        "download_url": "/dl/session-file.bin?token=abc",
        "expires_at": "2030-01-01T00:00:00Z",
        "file_name": "Video 1.mp4",
        "file_size": 123456,
    }
    return httpx.Response(200, json=payload)


SESSION_FILE_BINARY_CONTENT = b"SESSION_FILE_CONTENT"
SESSION_FILE_DEFAULT_NAME = "Video 1.mp4"


def handle_session_file_binary(request: httpx.Request) -> httpx.Response:
    # Respond with Content-Disposition to exercise header-based filename
    headers = {"content-disposition": f'attachment; filename="{SESSION_FILE_DEFAULT_NAME}"'}
    return httpx.Response(200, content=SESSION_FILE_BINARY_CONTENT, headers=headers)


def handle_session_zip_download_link(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200, json={"status": TASK_STATUS_PROCESSING, "message": None, "task_id": "zip-session-1"}
    )


def handle_session_csv_download_link(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200, json={"status": TASK_STATUS_PROCESSING, "message": None, "task_id": "csv-session-1"}
    )


# ---- Write handlers (CRUD + default records + duplicate files) ----
SESSION_ID_CREATED = 102
DEFAULT_RECORD_ID = 555
SESSION_DUPLICATE_FILENAME = "existing.mp4"


def _session_response_with(
    name: str = "Session A", release_level: str = "public", source_date: str | None = "2025-05-31"
) -> dict:
    session = _get_mock_session_1()
    session["name"] = name
    session["release_level"] = release_level
    session["source_date"] = source_date
    return session


def handle_session_create(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    response = _session_response_with(
        name=body.get("name", "Session A"),
        release_level=body.get("release_level", "public"),
        source_date=body.get("source_date"),
    )
    response["id"] = SESSION_ID_CREATED
    return httpx.Response(201, json=response)


def handle_session_put(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    return httpx.Response(
        200,
        json=_session_response_with(
            name=body.get("name", "Session A"),
            release_level=body.get("release_level") or "public",
            source_date=body.get("source_date"),
        ),
    )


def handle_session_patch(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    base = _get_mock_session_1()
    if "name" in body:
        base["name"] = body["name"]
    if "release_level" in body:
        base["release_level"] = body["release_level"]
    if "source_date" in body:
        base["source_date"] = body["source_date"]
    return httpx.Response(200, json=base)


def handle_session_delete(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def handle_session_add_default_record(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={})


def handle_session_remove_default_record(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def handle_session_check_duplicate_files(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    filenames = body.get("filenames", [])
    result = [{"filename": fn, "exists": fn == SESSION_DUPLICATE_FILENAME} for fn in filenames]
    return httpx.Response(200, json=result)


# ---- File metadata handlers ----
def _session_file_response_with(**overrides) -> dict:
    base = _get_mock_session_1_file()
    base.update(overrides)
    return base


def handle_session_file_put(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    return httpx.Response(200, json=_session_file_response_with(
        name=body.get("name") or "Video 1.mp4",
        release_level=body.get("release_level") or "public",
        source_date=body.get("source_date") or "2025-05-31",
    ))


def handle_session_file_patch(request: httpx.Request) -> httpx.Response:
    import json as _json

    body = _json.loads(request.content or b"{}")
    overrides = {k: v for k, v in body.items() if k in {"name", "release_level", "source_date"}}
    return httpx.Response(200, json=_session_file_response_with(**overrides))


def handle_session_file_delete(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def build_sessions_transport():
    return build_transport(
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/sessions/", handle_sessions_list),
        ("POST", f"/volumes/{VOLUME_ID_PRIMARY}/sessions/", handle_session_create),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/",
            handle_session_detail,
        ),
        (
            "PUT",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/",
            handle_session_put,
        ),
        (
            "PATCH",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/",
            handle_session_patch,
        ),
        (
            "DELETE",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/",
            handle_session_delete,
        ),
        (
            "POST",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/add-default-record/",
            handle_session_add_default_record,
        ),
        (
            "POST",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/remove-default-record/",
            handle_session_remove_default_record,
        ),
        (
            "POST",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/check-duplicate-files/",
            handle_session_check_duplicate_files,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/",
            handle_session_files_list,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{SESSION_FILE_ID_1}/",
            handle_session_file_detail,
        ),
        (
            "PUT",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{SESSION_FILE_ID_1}/",
            handle_session_file_put,
        ),
        (
            "PATCH",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{SESSION_FILE_ID_1}/",
            handle_session_file_patch,
        ),
        (
            "DELETE",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{SESSION_FILE_ID_1}/",
            handle_session_file_delete,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{SESSION_FILE_ID_1}/download-link/",
            handle_session_file_download_link,
        ),
        ("GET", "/dl/session-file.bin", handle_session_file_binary),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/download-link/",
            handle_session_zip_download_link,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/csv-download-link/",
            handle_session_csv_download_link,
        ),
    )


def build_composite_transport():
    """Composite transport with auth and sessions routes."""
    client_transport = build_client_transport()
    sessions_transport = build_sessions_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return sessions_transport.handle_request(request)

    return httpx.MockTransport(router)
