"""Tags fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .client import build_client_transport
from .common import build_transport
from .factory import make_page


def _get_mock_tag() -> dict:
    return {
        "id": 1,
        "name": "language",
    }


def _get_mock_tags_page() -> dict:
    return make_page(results=[_get_mock_tag()], count=1)


def handle_tags_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_tags_page())


def handle_tag_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_tag())


def build_tags_transport():
    return build_transport(
        ("GET", "/tags/", handle_tags_list),
        ("GET", "/tags/1/", handle_tag_detail),
    )


def build_composite_transport():
    client_transport = build_client_transport()
    tags_transport = build_tags_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return tags_transport.handle_request(request)

    return httpx.MockTransport(router)
