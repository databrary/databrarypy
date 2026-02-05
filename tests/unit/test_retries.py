from __future__ import annotations

import time

import httpx

from databrarypy.resources._base import BaseResource


def test_retry_after_header_is_honored(monkeypatch):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"detail": "slow down"}, headers={"Retry-After": "1"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url="https://api.example", transport=transport)

    def headers() -> dict[str, str]:
        return {}

    br = BaseResource(
        client,
        headers,
        None,
        max_retries=5,
        respect_retry_after=True,
        backoff_base=0.01,
        backoff_jitter=0.0,
    )

    t0 = time.time()
    data = br._raw_get_json("/x")
    dt = time.time() - t0
    assert data == {"ok": True}
    assert dt >= 1.0


def test_exponential_backoff_on_503_then_success():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503, json={"detail": "temporary"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url="https://api.example", transport=transport)

    def headers() -> dict[str, str]:
        return {}

    br = BaseResource(
        client,
        headers,
        None,
        max_retries=5,
        respect_retry_after=True,
        backoff_base=0.01,
        backoff_jitter=0.0,
    )
    data = br._raw_get_json("/x")
    assert data == {"ok": True}
