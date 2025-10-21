"""Volume tags, links, and fundings fixtures and handlers."""

from __future__ import annotations

import httpx

from .funders import MOCK_FUNDINGS_LIST

MOCK_VOLUME_TAGS_1 = ["research", "data", "sample", "test", "collection", "study"]

MOCK_VOLUME_LINK_1 = {
    "id": 51,
    "title": "Sample Research Article",
    "url": "https://example.org/research/sample-article",
}

MOCK_VOLUME_LINKS_1 = [MOCK_VOLUME_LINK_1]


def handle_volume_tags_1(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_VOLUME_TAGS_1)


def handle_volume_links_1(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_VOLUME_LINKS_1)


def handle_volume_fundings_1(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_FUNDINGS_LIST)
