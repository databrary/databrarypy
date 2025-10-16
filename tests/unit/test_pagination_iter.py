from __future__ import annotations

import httpx

from databrarypy.resources._base import BaseResource


def test_paginate_items_next_url_chain():
    pages = [
        {"count": 3, "next": "https://api.example/pg2", "previous": None, "results": [1]},
        {"count": 3, "next": "/pg3", "previous": None, "results": [2]},
        {"count": 3, "next": None, "previous": None, "results": [3]},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/pg1":
            return httpx.Response(200, json=pages[0])
        if request.url.path.endswith("/pg2"):
            return httpx.Response(200, json=pages[1])
        if request.url.path == "/pg3":
            return httpx.Response(200, json=pages[2])
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url="https://api.example", transport=transport)

    def headers() -> dict[str, str]:
        return {}

    br = BaseResource(client, headers, None)
    items = list(br.paginate_items("/pg1", parser=lambda x: x))
    assert items == [1, 2, 3]
