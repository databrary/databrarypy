"""UploadsResource tests (initiate / status / complete / upload_file)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from databrarypy.client import DatabraryClient
from databrarypy.errors import ApiError
from databrarypy.models.uploads import (
    InitiateMultipartResponse,
    InitiateSingleResponse,
    Part,
    UploadStatus,
)
from tests.fixtures.client import build_client_transport
from tests.fixtures.common import build_transport
from tests.fixtures.uploads import (
    PART_PUT_PATH_TEMPLATE,
    S3_UPLOAD_ID,
    SIGNED_PUT_PATH,
    STATUS_URL_PATH,
    UPLOAD_GUID,
    _multipart_initiate_payload,
    _single_initiate_payload,
    build_composite_transport,
    build_uploads_transport,
    handle_abort_multipart,
    handle_complete_multipart,
    handle_presign_parts,
    handle_s3_single_put,
    handle_status_completed,
    handle_status_infected,
    handle_status_scanning,
)


def _make_client(transport: httpx.BaseTransport) -> DatabraryClient:
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
# initiate
# ------------------------------------------------------------------


def test_initiate_single() -> None:
    client = _make_client(build_composite_transport())

    response = client.uploads.initiate(
        filename="small.txt",
        destination_type="session",
        object_id=42,
        file_size=10,
        content_type="text/plain",
    )
    assert isinstance(response, InitiateSingleResponse)
    assert response.signed_upload_url == SIGNED_PUT_PATH
    assert response.status_url == STATUS_URL_PATH
    assert "x-amz-server-side-encryption" in response.required_headers


def test_initiate_multipart_via_large_size() -> None:
    client = _make_client(build_composite_transport())

    response = client.uploads.initiate(
        filename="big.bin",
        destination_type="folder",
        object_id=7,
        file_size=200 * 1024 * 1024,
    )
    assert isinstance(response, InitiateMultipartResponse)
    assert response.upload_guid == UPLOAD_GUID
    assert response.s3_upload_id == S3_UPLOAD_ID
    assert len(response.part_urls) == 2


def test_initiate_core_payload_without_upload_type() -> None:
    """Plain core returns single-upload fields without ``upload_type``; client injects it."""

    def handle_initiate_core(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "signed_upload_url": SIGNED_PUT_PATH,
                "status_url": STATUS_URL_PATH,
                "required_headers": {},
            },
        )

    base = build_uploads_transport()
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return handle_initiate_core(request)
        return base.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    response = client.uploads.initiate(filename="x.bin", destination_type="session", object_id=1)
    assert isinstance(response, InitiateSingleResponse)
    assert response.upload_type == "single"


def test_initiate_includes_source_ids_in_json_body() -> None:
    received: dict = {}

    def handle_initiate_capture(request: httpx.Request) -> httpx.Response:
        import json as _json

        received.update(_json.loads(request.content or b"{}"))
        return httpx.Response(201, json=_single_initiate_payload())

    base = build_uploads_transport()
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return handle_initiate_capture(request)
        return base.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    client.uploads.initiate(
        filename="a.mp4",
        destination_type="folder",
        object_id=99,
        source_session_id=11,
        source_folder_id=22,
    )
    assert received["source_session_id"] == 11
    assert received["source_folder_id"] == 22


# ------------------------------------------------------------------
# status
# ------------------------------------------------------------------


def test_status() -> None:
    client = _make_client(build_composite_transport())

    assert client.uploads.status(UPLOAD_GUID) == "completed"


def test_status_raises_api_error_when_response_not_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _make_client(build_composite_transport())
    monkeypatch.setattr(client.uploads, "_get_json", lambda *_a, **_k: [])

    with pytest.raises(ApiError, match="Unexpected status response shape"):
        client.uploads.status(UPLOAD_GUID)


# ------------------------------------------------------------------
# complete (multipart only)
# ------------------------------------------------------------------


def test_complete_multipart() -> None:
    client = _make_client(build_composite_transport())

    result = client.uploads.complete(
        UPLOAD_GUID,
        s3_upload_id=S3_UPLOAD_ID,
        parts=[
            Part(part_number=1, etag="part-1-etag"),
            Part(part_number=2, etag="part-2-etag"),
        ],
    )
    assert result == {"status": "completed"}


def test_complete_accepts_dict_parts() -> None:
    client = _make_client(build_composite_transport())

    result = client.uploads.complete(
        UPLOAD_GUID,
        s3_upload_id=S3_UPLOAD_ID,
        parts=[{"part_number": 1, "etag": "x"}],
    )
    assert result["status"] == "completed"


def test_complete_raises_api_error_when_response_not_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _make_client(build_composite_transport())
    real_post = client.uploads._post_json

    def fake_post(path: str, **kwargs: object) -> object:
        if path == "/uploads/complete-multipart/":
            return []
        return real_post(path, **kwargs)  # type: ignore[arg-type,misc]

    monkeypatch.setattr(client.uploads, "_post_json", fake_post)

    with pytest.raises(ApiError, match="complete-multipart endpoint"):
        client.uploads.complete(
            UPLOAD_GUID,
            s3_upload_id=S3_UPLOAD_ID,
            parts=[Part(part_number=1, etag="a")],
        )


# ------------------------------------------------------------------
# presign_parts / abort
# ------------------------------------------------------------------


def test_presign_parts() -> None:
    client = _make_client(build_composite_transport())

    urls = client.uploads.presign_parts(UPLOAD_GUID, S3_UPLOAD_ID, [1, 2, 3])
    assert [u.part_number for u in urls] == [1, 2, 3]
    assert urls[0].url == PART_PUT_PATH_TEMPLATE.format(n=1)


def test_presign_parts_raises_api_error_when_response_not_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _make_client(build_composite_transport())
    real_post = client.uploads._post_json

    def fake_post(path: str, **kwargs: object) -> object:
        if path == "/uploads/presign-parts/":
            return "bad"
        return real_post(path, **kwargs)  # type: ignore[arg-type,misc]

    monkeypatch.setattr(client.uploads, "_post_json", fake_post)

    with pytest.raises(ApiError, match="presign-parts endpoint"):
        client.uploads.presign_parts(UPLOAD_GUID, S3_UPLOAD_ID, [1])


def test_abort_multipart() -> None:
    client = _make_client(build_composite_transport())

    assert client.uploads.abort_multipart(UPLOAD_GUID, S3_UPLOAD_ID) is None


# ------------------------------------------------------------------
# upload_file (orchestration)
# ------------------------------------------------------------------


def test_upload_file_single(tmp_path: Path) -> None:
    client = _make_client(build_composite_transport())

    f = tmp_path / "tiny.txt"
    f.write_bytes(b"hello world")

    result = client.uploads.upload_file(
        f,
        destination_type="session",
        object_id=42,
        poll_interval=0.0,
    )
    assert result.upload_type == "single"
    assert result.final_status == "completed"


def test_upload_file_poll_status_false_skips_poll(tmp_path: Path) -> None:
    client = _make_client(build_composite_transport())

    f = tmp_path / "x.txt"
    f.write_bytes(b"x")

    result = client.uploads.upload_file(
        f,
        destination_type="session",
        object_id=1,
        poll_status=False,
    )
    assert result.final_status == ""
    assert result.upload_type == "single"


def test_upload_file_passes_explicit_content_type_to_initiate(tmp_path: Path) -> None:
    captured: dict = {}

    def handle_capture(request: httpx.Request) -> httpx.Response:
        import json as _json

        captured.update(_json.loads(request.content or b"{}"))
        return httpx.Response(201, json=_single_initiate_payload())

    base = build_uploads_transport()
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return handle_capture(request)
        return base.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    f = tmp_path / "doc.xyz"  # unlikely default mime
    f.write_bytes(b"data")

    client.uploads.upload_file(
        f,
        destination_type="folder",
        object_id=3,
        content_type="application/pdf",
        poll_status=False,
    )
    assert captured["content_type"] == "application/pdf"


def test_upload_file_stops_on_infected_status(tmp_path: Path) -> None:
    client = _make_client(build_composite_transport(status_handler=handle_status_infected))
    f = tmp_path / "t.bin"
    f.write_bytes(b"a")
    result = client.uploads.upload_file(
        f,
        destination_type="session",
        object_id=1,
        poll_interval=0.0,
    )
    assert result.final_status == UploadStatus.INFECTED.value


def test_upload_file_stops_on_upload_failed_terminal_status(tmp_path: Path) -> None:
    def handle_failed(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": UploadStatus.UPLOAD_FAILED.value})

    client = _make_client(build_composite_transport(status_handler=handle_failed))
    f = tmp_path / "t.bin"
    f.write_bytes(b"a")
    result = client.uploads.upload_file(
        f,
        destination_type="session",
        object_id=1,
        poll_interval=0.0,
    )
    assert result.final_status == UploadStatus.UPLOAD_FAILED.value


def test_upload_file_poll_times_out_while_scanning(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _make_client(build_composite_transport(status_handler=handle_status_scanning))
    f = tmp_path / "t.bin"
    f.write_bytes(b"x")
    with caplog.at_level("WARNING"):
        result = client.uploads.upload_file(
            f,
            destination_type="session",
            object_id=1,
            poll_interval=0.01,
            poll_timeout=0.05,
        )
    assert result.final_status == "scanning"
    assert "timed out" in caplog.text


def test_upload_file_status_json_not_dict_uses_timeout(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Non-object JSON from status endpoint yields empty status until timeout."""

    def handle_status_list(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    uploads = build_uploads_transport(status_handler=handle_status_list)
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return uploads.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    f = tmp_path / "t.bin"
    f.write_bytes(b"y")
    with caplog.at_level("WARNING"):
        result = client.uploads.upload_file(
            f,
            destination_type="session",
            object_id=1,
            poll_interval=0.01,
            poll_timeout=0.05,
        )
    assert result.final_status == ""
    assert "timed out" in caplog.text


def test_upload_file_multipart(tmp_path: Path) -> None:
    """Force a multipart flow by stubbing initiate to return the multipart payload."""

    def initiate_multipart(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=_multipart_initiate_payload(part_count=2, part_size=4))

    base_transport = build_uploads_transport(multipart_parts=2)
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return initiate_multipart(request)
        return base_transport.handle_request(request)

    client = _make_client(httpx.MockTransport(router))

    f = tmp_path / "big.bin"
    f.write_bytes(b"AAAABBBB")  # 8 bytes = 2 parts of 4 bytes each

    result = client.uploads.upload_file(
        f,
        destination_type="folder",
        object_id=7,
        poll_interval=0.0,
    )
    assert result.upload_type == "multipart"
    assert result.upload_guid == UPLOAD_GUID
    assert result.final_status == "completed"


def test_upload_file_multipart_empty_file_breaks_before_any_put(tmp_path: Path) -> None:
    """First ``read`` is empty: loop breaks without uploading (exercises ``break`` path)."""

    def initiate_multipart(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=_multipart_initiate_payload(part_count=2, part_size=4))

    base_transport = build_uploads_transport(multipart_parts=2)
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return initiate_multipart(request)
        return base_transport.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    f = tmp_path / "empty.bin"
    f.write_bytes(b"")

    result = client.uploads.upload_file(
        f,
        destination_type="folder",
        object_id=1,
        poll_status=False,
    )
    assert result.upload_type == "multipart"


def test_upload_file_multipart_rejects_file_larger_than_part_url_coverage(
    tmp_path: Path,
) -> None:
    def initiate_multipart(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=_multipart_initiate_payload(part_count=2, part_size=4))

    base_transport = build_uploads_transport(multipart_parts=2)
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return initiate_multipart(request)
        return base_transport.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    f = tmp_path / "too_big.bin"
    f.write_bytes(b"AAAABBBBCC")  # 10 bytes but only 2 parts of 4

    with pytest.raises(ValueError, match="more data than the server-provided part URLs"):
        client.uploads.upload_file(
            f,
            destination_type="folder",
            object_id=7,
            poll_status=False,
        )


def test_upload_file_multipart_reads_etag_from_lowercase_header(tmp_path: Path) -> None:
    """S3 may return ``etag`` (lowercase) without ``ETag``."""

    def initiate_one_part(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=_multipart_initiate_payload(part_count=1, part_size=1024))

    def handle_part_lowercase_etag(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"etag": '"lc-etag"'})

    uploads_rest = build_transport(
        ("GET", STATUS_URL_PATH, handle_status_completed),
        ("PUT", SIGNED_PUT_PATH, handle_s3_single_put),
        ("POST", "/uploads/complete-multipart/", handle_complete_multipart),
        ("POST", "/uploads/presign-parts/", handle_presign_parts),
        ("POST", "/uploads/abort-multipart/", handle_abort_multipart),
        ("PUT", PART_PUT_PATH_TEMPLATE.format(n=1), handle_part_lowercase_etag),
    )
    client_transport = build_client_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return initiate_one_part(request)
        return uploads_rest.handle_request(request)

    client = _make_client(httpx.MockTransport(router))
    f = tmp_path / "one.bin"
    f.write_bytes(b"hello")

    result = client.uploads.upload_file(
        f, destination_type="session", object_id=5, poll_status=False
    )
    assert result.upload_type == "multipart"


def test_upload_file_missing_path(tmp_path: Path) -> None:
    client = _make_client(build_composite_transport())

    with pytest.raises(FileNotFoundError):
        client.uploads.upload_file(
            tmp_path / "missing.bin",
            destination_type="session",
            object_id=1,
        )
