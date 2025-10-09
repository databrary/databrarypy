"""Institutions fixtures and mock handlers."""

import httpx

from .common import build_transport
from .factory import make_page

# ---- Top-level objects ----
MOCK_AVATAR_PNG = b"\x89PNG\r\n\x1a\n"

MOCK_INSTITUTION_PENN_STATE = {
    "id": 12,
    "name": "Penn State",
    "url": "https://psu.edu",
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

MOCK_INVESTIGATOR_USER = {
    "id": 1837,
    "firstName": "Test",
    "lastName": "Investigator",
    "email": "investigator@example.org",
    "affiliation": {"id": 12, "name": "Penn State"},
    "hasAvatar": False,
    "isAuthorizedInvestigator": True,
}

MOCK_INSTITUTION_12_AFFILIATE_INVESTIGATOR = {
    "role": "investigator",
    "user": MOCK_INVESTIGATOR_USER,
}

# ---- Paged payloads ----
MOCK_INSTITUTIONS_PAGE = make_page(
    results=[MOCK_INSTITUTION_PENN_STATE],
    total_pages=1,
    current_page=1,
    sort_by=None,
    sort_order="asc",
)

MOCK_INSTITUTION_12_AFFILIATES_PAGE = make_page(
    results=[MOCK_INSTITUTION_12_AFFILIATE_INVESTIGATOR],
    count=1,
)

MOCK_NOT_FOUND = {"detail": "Not found"}


def handle_institutions_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_INSTITUTIONS_PAGE)


def handle_institution_retrieve(request: httpx.Request) -> httpx.Response:
    # Return the first item
    return httpx.Response(200, json=MOCK_INSTITUTION_PENN_STATE)


def handle_institutions_affiliates(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_INSTITUTION_12_AFFILIATES_PAGE)


def handle_institution_avatar(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=MOCK_AVATAR_PNG)


def handle_institution_avatar_404(request: httpx.Request) -> httpx.Response:
    return httpx.Response(404, json=MOCK_NOT_FOUND)


def build_institutions_transport():
    return build_transport(
        ("GET", "/institutions/", handle_institutions_list),
        ("GET", "/institutions/12/", handle_institution_retrieve),
        ("GET", "/institutions/12/affiliates/", handle_institutions_affiliates),
        ("GET", "/institutions/12/avatar/", handle_institution_avatar),
        ("GET", "/institutions/999/avatar/", handle_institution_avatar_404),
    )
