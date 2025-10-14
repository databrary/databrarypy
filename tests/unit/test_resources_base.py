"""Tests for BaseResource HTTP helper methods."""

from __future__ import annotations

from pathlib import Path

import httpx

from databrarypy.resources._base import BaseResource


def test_build_params_filters_and_bools():
    params = BaseResource.build_params(a=1, b=None, c=True, d=False, e="x")
    assert params == {"a": 1, "c": "true", "d": "false", "e": "x"}


def test_get_json_and_bytes_methods():
    def handle_json(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/json":
            return httpx.Response(200, json={"ok": True})
        if request.url.path == "/bytes":
            return httpx.Response(200, content=b"data")
        if request.url.path == "/bytes-missing":
            return httpx.Response(404, json={"detail": "missing"})
        return httpx.Response(500)

    transport = httpx.MockTransport(handle_json)
    client = httpx.Client(base_url="https://api.example", transport=transport)

    def headers() -> dict[str, str]:
        return {"X": "y"}

    # Instantiate a minimal BaseResource to exercise helper methods
    br = BaseResource(client, headers, lambda d: d)
    data = br._raw_get_json("/json")
    assert data == {"ok": True}
    content = br._download_bytes("/bytes")
    assert content == b"data"
    empty = br._download_bytes("/bytes-missing")
    assert empty == b""


def test_download_to_path_and_filename_resolution(tmp_path: Path):
    # Handlers to exercise header filename and URL basename fallback
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/with-header":
            headers = {"content-disposition": 'attachment; filename="file-header.bin"'}
            return httpx.Response(200, content=b"data", headers=headers)
        if request.url.path == "/no-header.bin":
            # no content-disposition; URL basename should be used
            return httpx.Response(200, content=b"data")
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url="https://api.example", transport=transport)

    def headers() -> dict[str, str]:
        return {}

    br = BaseResource(client, headers, None)

    # Save to a directory with header-provided filename
    out_dir = tmp_path / "dl1"
    out_dir.mkdir(parents=True, exist_ok=True)
    p1 = br._download_to_path("/with-header", str(out_dir))
    assert p1.endswith("file-header.bin")

    # Save to a directory without header: uses URL basename
    out_dir2 = tmp_path / "dl2"
    out_dir2.mkdir(parents=True, exist_ok=True)
    p2 = br._download_to_path("/no-header.bin", str(out_dir2))
    assert p2.endswith("no-header.bin")

    # Save to an explicit file path
    explicit = tmp_path / "explicit.bin"
    p3 = br._download_to_path("/with-header", str(explicit))
    assert p3 == str(explicit)
