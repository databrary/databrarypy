"""Sponsorship fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .common import build_transport
from .data_constants import (
    INSTITUTION_SPONSORSHIP_ID_1,
    SPONSORSHIP_ID_1,
)
from .factory import make_page
from .institutions import MOCK_INSTITUTION_1, MOCK_INSTITUTION_1_DETAILED
from .users import MOCK_USER_1, MOCK_USER_OWNER


# ---- Sponsorship objects ----
def _get_mock_sponsorship_1():
    """Get mock sponsorship (lazy to avoid issues with dict copying)."""
    return {
        "id": SPONSORSHIP_ID_1,
        "sponsor": MOCK_USER_1,
        "user": MOCK_USER_1,
        "institution": MOCK_INSTITUTION_1,
        "access_level": "read",
        "has_databrary_affiliate_access": False,
        "sponsor_institution_connection": 999,
        "expiration_date": "2030-12-31",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-06-01T12:30:00Z",
    }


def _get_mock_institution_sponsorship_1():
    """Get mock institution sponsorship (lazy to avoid issues with dict copying)."""
    return {
        "id": INSTITUTION_SPONSORSHIP_ID_1,
        "institution": MOCK_INSTITUTION_1_DETAILED,
        "user": MOCK_USER_OWNER,
        "role": "investigator",
        "expiration_date": "2026-03-05",
        "created_at": "2025-03-05T16:06:15.028482Z",
        "updated_at": "2025-03-05T16:06:15.028493Z",
        "request": None,
    }


# ---- Paged payloads ----
def _get_mock_sponsorships_page():
    return make_page(
        results=[_get_mock_sponsorship_1()],
        total_pages=1,
        current_page=1,
        sort_by=None,
        sort_order="asc",
    )


MOCK_SPONSORSHIPS_PAGE = _get_mock_sponsorships_page()


def _get_mock_institution_12_affiliate_investigator():
    from .users import MOCK_USER_1

    return {
        "role": "investigator",
        "user": MOCK_USER_1,
    }


def handle_sponsorships_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_sponsorships_page())


def handle_sponsorship_retrieve(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_sponsorship_1())


def build_sponsorships_transport():
    return build_transport(
        ("GET", "/sponsorships/", handle_sponsorships_list),
        ("GET", f"/sponsorships/{SPONSORSHIP_ID_1}/", handle_sponsorship_retrieve),
    )
