"""Search fixtures and mock handlers for users, institutions, and volumes."""

from __future__ import annotations

import httpx

from .client import build_client_transport
from .common import build_transport
from .factory import make_page


def _get_mock_user_hit() -> dict:
    return {
        "id": 6,
        "first_name": "Alex",
        "last_name": "Doe",
        "full_name": "Alex Doe",
        "email": "alex@example.org",
        "orcid": None,
        "url": None,
        "is_authorized": True,
        "has_avatar": False,
        "score": 1.0,
    }


def _get_mock_institution_hit() -> dict:
    return {
        "id": 101,
        "name": "Example University",
        "url": "https://example.org",
        "has_avatar": True,
        "score": 0.9,
    }


def _get_mock_volume_hit() -> dict:
    return {
        "id": 1001,
        "title": "Language Development",
        "description": "A study on early language acquisition",
        "owner": {
            "user_id": 6,
            "full_name": "Alex Doe",
            "institution_name": "Example University",
        },
        "tags": ["language", "development"],
        "file_types": ["audio", "video"],
        "has_session": True,
        "sharing_level": "public",
        "score": 0.95,
    }


def _page(data: dict) -> dict:
    return make_page(results=[data], count=1)


def handle_search_users(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_page(_get_mock_user_hit()))


def handle_search_institutions(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_page(_get_mock_institution_hit()))


def handle_search_volumes(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_page(_get_mock_volume_hit()))


def build_search_transport():
    return build_transport(
        ("GET", "/search/users/", handle_search_users),
        ("GET", "/search/institutions/", handle_search_institutions),
        ("GET", "/search/volumes/", handle_search_volumes),
    )


def build_composite_transport():
    client_transport = build_client_transport()
    search_transport = build_search_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return search_transport.handle_request(request)

    return httpx.MockTransport(router)
