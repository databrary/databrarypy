"""Tests for BaseResource HTTP helper methods."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from databrarypy.errors import (
    ApiError,
    ForbiddenError,
    NotFoundError,
    ServerError,
    UnauthorizedError,
)
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


# --- Additional BaseResource coverage ---


def _br_with_transport(handler: httpx.MockTransport) -> BaseResource:
    client = httpx.Client(base_url="https://api.example", transport=handler)

    def headers() -> dict[str, str]:
        return {}

    return BaseResource(
        client,
        headers,
        None,
        max_retries=1,
        respect_retry_after=True,
        backoff_base=0.001,
        backoff_jitter=0.0,
    )


def test_request_json_empty_body_returns_empty_dict():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(204, content=b"")

    br = _br_with_transport(httpx.MockTransport(handler))
    data = br._raw_get_json("/empty")
    assert data == {}


@pytest.mark.parametrize(
    "code, exc",
    [(401, UnauthorizedError), (403, ForbiddenError), (404, NotFoundError)],
)
def test_request_json_maps_auth_and_not_found_errors(code, exc):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(code, json={"detail": "x"})

    br = _br_with_transport(httpx.MockTransport(handler))
    with pytest.raises(exc):
        br._raw_get_json("/x")


def test_request_json_generic_400_raises_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"detail": "bad"})

    br = _br_with_transport(httpx.MockTransport(handler))
    with pytest.raises(ApiError):
        br._raw_get_json("/x")


def test_request_json_429_no_retries_raises_rate_limit_error():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(429, text="slow", headers={"Retry-After": "2"})

    # max_retries=0 to surface the RateLimitError immediately
    client = httpx.Client(base_url="https://api.example", transport=httpx.MockTransport(handler))

    def headers() -> dict[str, str]:
        return {}

    br = BaseResource(client, headers, None, max_retries=0, respect_retry_after=True)
    with pytest.raises(Exception) as exc:
        br._raw_get_json("/x")
    # ensure our handler was called exactly once and we raised a typed error
    assert calls["n"] == 1
    assert exc.type.__name__ == "RateLimitError"


def test_request_json_transport_error_exhaustion_raises_server_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TransportError("boom")

    br = _br_with_transport(httpx.MockTransport(handler))
    with pytest.raises(ServerError):
        br._raw_get_json("/x")


def test_request_json_503_exhausted_raises_server_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "temporary"})

    br = _br_with_transport(httpx.MockTransport(handler))
    with pytest.raises(ServerError):
        br._raw_get_json("/x")


def test_request_json_500_retry_then_success():
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(500, text="err")
        return httpx.Response(200, json={"ok": True})

    br = _br_with_transport(httpx.MockTransport(handler))
    data = br._raw_get_json("/x")
    assert data == {"ok": True} and calls["n"] == 2


def test_request_json_500_no_retry_raises_server_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="err")

    # no retries to hit the fallback 5xx raise branch
    client = httpx.Client(base_url="https://api.example", transport=httpx.MockTransport(handler))

    def headers() -> dict[str, str]:
        return {}

    br = BaseResource(client, headers, None, max_retries=0)
    with pytest.raises(ServerError):
        br._raw_get_json("/x")


def test_request_json_429_with_non_numeric_retry_after_is_ignored_then_success():
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"detail": "slow"}, headers={"Retry-After": "abc"})
        return httpx.Response(200, json={"ok": True})

    br = _br_with_transport(httpx.MockTransport(handler))
    data = br._raw_get_json("/x")
    assert data == {"ok": True}


def test_put_json_empty_body_returns_empty_dict():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "PUT":
            return httpx.Response(204, content=b"")
        return httpx.Response(404)

    br = _br_with_transport(httpx.MockTransport(handler))
    data = br._put_json("/resource/1/", json={"name": "x"})
    assert data == {}


def test_get_json_or_none_parse_error_on_non_204_returns_none():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    br = _br_with_transport(httpx.MockTransport(handler))
    assert br._get_json_or_none("/stats/") is None


def test_compute_delay_with_jitter_is_non_negative():
    br = _br_with_transport(httpx.MockTransport(lambda r: httpx.Response(404)))
    br._backoff_jitter = 0.5
    delay = br._compute_delay(attempt=2)
    assert delay >= br._backoff_base * (2**2)


def test_get_page_normalizes_missing_count():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/p1":
            # Return result list without count
            return httpx.Response(200, json={"results": [1, 2]})
        return httpx.Response(404)

    br = _br_with_transport(httpx.MockTransport(handler))
    page = br._get_page("/p1")
    assert page.count == 2 and page.results == [1, 2]
