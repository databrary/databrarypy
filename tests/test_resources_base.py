"""Tests for BaseResource HTTP helper methods."""

from __future__ import annotations

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
    content = br._get_bytes_or_empty("/bytes")
    assert content == b"data"
    empty = br._get_bytes_or_empty("/bytes-missing")
    assert empty == b""
