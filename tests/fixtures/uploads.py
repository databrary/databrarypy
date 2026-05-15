"""Uploads fixtures and mock handlers (initiate / S3 PUT / status / complete)."""

from __future__ import annotations

import json as _json

import httpx

from .client import build_client_transport
from .common import build_transport

# ---- IDs / constants ----
UPLOAD_GUID = "11111111-2222-3333-4444-555555555555"
S3_UPLOAD_ID = "s3-upload-abc"
STATUS_URL_PATH = f"/uploads/{UPLOAD_GUID}/status/"
SIGNED_PUT_PATH = f"/s3-fake/{UPLOAD_GUID}/single"
PART_PUT_PATH_TEMPLATE = f"/s3-fake/{UPLOAD_GUID}/part-{{n}}"
SMALL_THRESHOLD = 100 * 1024 * 1024  # mirrors server


def _single_initiate_payload() -> dict:
    return {
        "upload_type": "single",
        "signed_upload_url": SIGNED_PUT_PATH,
        "required_headers": {
            "Content-Type": "application/octet-stream",
            "x-amz-server-side-encryption": "aws:kms",
        },
        "status_url": STATUS_URL_PATH,
    }


def _multipart_initiate_payload(part_count: int = 2, part_size: int = 4) -> dict:
    return {
        "upload_type": "multipart",
        "upload_guid": UPLOAD_GUID,
        "s3_upload_id": S3_UPLOAD_ID,
        "part_urls": [
            {"part_number": n, "url": PART_PUT_PATH_TEMPLATE.format(n=n)}
            for n in range(1, part_count + 1)
        ],
        "part_size": part_size,
        "status_url": STATUS_URL_PATH,
    }


def handle_initiate_single(request: httpx.Request) -> httpx.Response:
    body = _json.loads(request.content or b"{}")
    if body.get("file_size") and int(body["file_size"]) >= SMALL_THRESHOLD:
        # Server-side decision: multipart for large files
        return httpx.Response(201, json=_multipart_initiate_payload())
    return httpx.Response(201, json=_single_initiate_payload())


def handle_status_completed(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"status": "completed"})


def handle_s3_single_put(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, headers={"ETag": '"single-etag"'})


def handle_s3_part_put_factory(part_number: int):
    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"ETag": f'"part-{part_number}-etag"'})

    return _handler


def handle_complete_multipart(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"status": "completed"})


def handle_presign_parts(request: httpx.Request) -> httpx.Response:
    body = _json.loads(request.content or b"{}")
    nums = body.get("part_numbers", [])
    return httpx.Response(
        200,
        json={
            "part_urls": [
                {"part_number": n, "url": PART_PUT_PATH_TEMPLATE.format(n=n)} for n in nums
            ]
        },
    )


def handle_abort_multipart(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def build_uploads_transport(*, multipart_parts: int = 2):
    routes = [
        ("POST", "/uploads/initiate/", handle_initiate_single),
        ("GET", STATUS_URL_PATH, handle_status_completed),
        ("PUT", SIGNED_PUT_PATH, handle_s3_single_put),
        ("POST", "/uploads/complete-multipart/", handle_complete_multipart),
        ("POST", "/uploads/presign-parts/", handle_presign_parts),
        ("POST", "/uploads/abort-multipart/", handle_abort_multipart),
    ]
    for n in range(1, multipart_parts + 1):
        routes.append(("PUT", PART_PUT_PATH_TEMPLATE.format(n=n), handle_s3_part_put_factory(n)))
    return build_transport(*routes)


def build_composite_transport(*, multipart_parts: int = 2):
    client_transport = build_client_transport()
    uploads_transport = build_uploads_transport(multipart_parts=multipart_parts)

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return uploads_transport.handle_request(request)

    return httpx.MockTransport(router)
