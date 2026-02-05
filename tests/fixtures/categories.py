"""Categories fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .client import build_client_transport
from .common import build_transport
from .factory import make_page


def _get_mock_category() -> dict:
    # Constants for test expectations
    # Category
    CATEGORY_ID_1 = 1
    CATEGORY_NAME_1 = "Demographics"
    CATEGORY_DESCRIPTION_1 = "Participant demographics"
    # Metrics
    METRIC_ID_AGE = 10
    METRIC_NAME_AGE = "age"
    METRIC_ID_GENDER = 11
    METRIC_NAME_GENDER = "gender"

    return {
        "id": CATEGORY_ID_1,
        "name": CATEGORY_NAME_1,
        "description": CATEGORY_DESCRIPTION_1,
        "metrics": [
            {
                "id": METRIC_ID_AGE,
                "name": METRIC_NAME_AGE,
                "type": "number",
                "release": "public",
                "description": "Age in years",
                "required": False,
            },
            {
                "id": METRIC_ID_GENDER,
                "name": METRIC_NAME_GENDER,
                "type": "choice",
                "options": ["male", "female", "other"],
                "release": "public",
                "required": False,
            },
        ],
    }


def _get_mock_categories_page() -> dict:
    return make_page(results=[_get_mock_category()], count=1)


def handle_categories_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_categories_page())


def handle_category_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_category())


def build_categories_transport():
    return build_transport(
        ("GET", "/categories/", handle_categories_list),
        ("GET", "/categories/1/", handle_category_detail),
    )


def build_composite_transport():
    client_transport = build_client_transport()
    categories_transport = build_categories_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return categories_transport.handle_request(request)

    return httpx.MockTransport(router)
