"""Health endpoint smoke test via SystemResource.is_healthy()."""

import httpx

from databrarypy.client import DatabraryClient

from ..fixtures.client import build_client_transport
from ..fixtures.common import build_transport


def handle_health_ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"status": "ok"})


def handle_health_fail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(503, json={"status": "down"})


def build_health_transport(ok: bool = True) -> httpx.MockTransport:
    token_transport = build_client_transport()
    health_transport = build_transport(
        ("GET", "/health/", handle_health_ok if ok else handle_health_fail)
    )

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key == ("POST", "/o/token/"):
            return token_transport.handle_request(request)
        return health_transport.handle_request(request)

    return httpx.MockTransport(router)


def test_health_true():
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=build_health_transport(ok=True),
    )
    client.auth.login()
    assert client.system.is_healthy() is True


def test_health_false():
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=build_health_transport(ok=False),
    )
    client.auth.login()
    assert client.system.is_healthy() is False
