"""Institutions fixtures and mock handlers."""

import httpx

from .common import build_transport
from .data_constants import (
    INSTITUTION_ID_1,
    INSTITUTION_ID_2,
    INSTITUTION_ID_3,
    INSTITUTION_ID_NOT_FOUND,
    MOCK_AVATAR_PNG,
)
from .factory import make_page

MOCK_INSTITUTION_1 = {
    "id": INSTITUTION_ID_1,
    "name": "Example University",
    "url": "https://example.edu",
    "date_signed": "2020-01-01",
    "source": "user",
    "created_at": None,
    "updated_at": None,
    "has_avatar": False,
    "has_administrators": True,
    "latitude": None,
    "longitude": None,
    "manual_coordinates": False,
}

MOCK_INSTITUTION_1_DETAILED = {
    "id": INSTITUTION_ID_1,
    "name": "Example University, Main Campus",
    "url": "https://example.edu",
    "date_signed": "2025-03-05",
    "source": "admin",
    "created_at": "2025-03-05T16:04:01.655967Z",
    "updated_at": "2025-05-27T13:26:37.830779Z",
    "has_avatar": True,
    "has_administrators": False,
    "latitude": 40.0,
    "longitude": -75.0,
    "manual_coordinates": False,
}

MOCK_INSTITUTION_2 = {
    "id": INSTITUTION_ID_2,
    "name": "Test Research Institute",
    "url": None,
    "date_signed": "2025-03-05",
    "source": "migration",
    "created_at": "2025-03-05T16:04:06.585189Z",
    "updated_at": "2025-03-05T16:04:06.585199Z",
    "has_avatar": False,
    "has_administrators": False,
    "latitude": None,
    "longitude": None,
    "manual_coordinates": False,
}

MOCK_INSTITUTION_3 = {
    "id": INSTITUTION_ID_3,
    "name": "Sample Academic Institution",
    "url": None,
    "date_signed": "2025-03-05",
    "source": "migration",
    "created_at": "2025-03-05T16:04:07.179887Z",
    "updated_at": "2025-03-05T16:04:07.179897Z",
    "has_avatar": False,
    "has_administrators": False,
    "latitude": None,
    "longitude": None,
    "manual_coordinates": False,
}


# ---- Paged payloads ----
MOCK_INSTITUTIONS_PAGE = make_page(
    results=[MOCK_INSTITUTION_1],
    total_pages=1,
    current_page=1,
    sort_by=None,
    sort_order="asc",
)


def _get_institution_12_affiliates_page():
    from .sponsorships import _get_mock_institution_12_affiliate_investigator

    return make_page(
        results=[_get_mock_institution_12_affiliate_investigator()],
        count=1,
    )


MOCK_NOT_FOUND = {"detail": "Not found"}


def handle_institutions_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_INSTITUTIONS_PAGE)


def handle_institution_retrieve(request: httpx.Request) -> httpx.Response:
    # Return the Example University institution
    return httpx.Response(200, json=MOCK_INSTITUTION_1)


def handle_institutions_affiliates(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_institution_12_affiliates_page())


def handle_institution_avatar(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=MOCK_AVATAR_PNG)


def handle_institution_avatar_404(request: httpx.Request) -> httpx.Response:
    return httpx.Response(404, json=MOCK_NOT_FOUND)


def build_institutions_transport():
    return build_transport(
        ("GET", "/institutions/", handle_institutions_list),
        ("GET", f"/institutions/{INSTITUTION_ID_1}/", handle_institution_retrieve),
        (
            "GET",
            f"/institutions/{INSTITUTION_ID_1}/affiliates/",
            handle_institutions_affiliates,
        ),
        ("GET", f"/institutions/{INSTITUTION_ID_1}/avatar/", handle_institution_avatar),
        ("GET", f"/institutions/{INSTITUTION_ID_NOT_FOUND}/avatar/", handle_institution_avatar_404),
    )
