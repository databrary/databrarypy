"""UploadsResource tests (initiate / status / complete / upload_file)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from databrarypy.client import DatabraryClient
from databrarypy.models.uploads import (
    InitiateMultipartResponse,
    InitiateSingleResponse,
    Part,
)
from tests.fixtures.uploads import (
    PART_PUT_PATH_TEMPLATE,
    S3_UPLOAD_ID,
    SIGNED_PUT_PATH,
    STATUS_URL_PATH,
    UPLOAD_GUID,
    _multipart_initiate_payload,
    build_composite_transport,
    build_uploads_transport,
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


# ------------------------------------------------------------------
# status
# ------------------------------------------------------------------


def test_status() -> None:
    client = _make_client(build_composite_transport())

    assert client.uploads.status(UPLOAD_GUID) == "completed"


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


# ------------------------------------------------------------------
# presign_parts / abort
# ------------------------------------------------------------------


def test_presign_parts() -> None:
    client = _make_client(build_composite_transport())

    urls = client.uploads.presign_parts(UPLOAD_GUID, S3_UPLOAD_ID, [1, 2, 3])
    assert [u.part_number for u in urls] == [1, 2, 3]
    assert urls[0].url == PART_PUT_PATH_TEMPLATE.format(n=1)


def test_abort_multipart() -> None:
    client = _make_client(build_composite_transport())

    assert client.uploads.abort_multipart(UPLOAD_GUID, S3_UPLOAD_ID) is True


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


def test_upload_file_multipart(tmp_path: Path) -> None:
    """Force a multipart flow by stubbing initiate to return the multipart payload."""

    def initiate_multipart(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=_multipart_initiate_payload(part_count=2, part_size=4))

    base_transport = build_uploads_transport(multipart_parts=2)
    from tests.fixtures.client import build_client_transport as _bct

    client_transport = _bct()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("POST", "/uploads/initiate/"):
            return initiate_multipart(request)
        return base_transport.handle_request(request)

    client = _make_client(httpx.MockTransport(router))

    f = tmp_path / "big.bin"
    f.write_bytes(b"AAAABBBBCC")  # 10 bytes, split into 4+4+2 → only 2 parts mocked

    result = client.uploads.upload_file(
        f,
        destination_type="folder",
        object_id=7,
        poll_interval=0.0,
    )
    assert result.upload_type == "multipart"
    assert result.upload_guid == UPLOAD_GUID
    assert result.final_status == "completed"


def test_upload_file_missing_path(tmp_path: Path) -> None:
    client = _make_client(build_composite_transport())

    with pytest.raises(FileNotFoundError):
        client.uploads.upload_file(
            tmp_path / "missing.bin",
            destination_type="session",
            object_id=1,
        )
