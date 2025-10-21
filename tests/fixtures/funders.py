"""Funder fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .common import build_transport
from .factory import make_page

# ---- Funder objects ----
MOCK_FUNDER_NSF = {
    "id": 1,
    "name": "Example Research Foundation (ERF)",
    "is_approved": True,
}

MOCK_FUNDER_NICHD = {
    "id": 3,
    "name": "Sample Funding Agency (SFA)",
    "is_approved": True,
}

# ---- Funding objects ----
MOCK_FUNDING_NSF = {
    "funder": MOCK_FUNDER_NSF,
    "awards": "ABC-1234567",
}

MOCK_FUNDING_NICHD = {
    "funder": MOCK_FUNDER_NICHD,
    "awards": "XYZ-9876543",
}

MOCK_FUNDINGS_LIST = [
    MOCK_FUNDING_NSF,
    MOCK_FUNDING_NICHD,
]

# ---- Paged payloads ----
MOCK_FUNDERS_PAGE = make_page(
    results=[MOCK_FUNDER_NSF, MOCK_FUNDER_NICHD],
    total_pages=1,
    current_page=1,
    sort_by=None,
    sort_order="asc",
)


def handle_funders_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_FUNDERS_PAGE)


def handle_funder_retrieve(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_FUNDER_NSF)


def build_funders_transport():
    return build_transport(
        ("GET", "/funders/", handle_funders_list),
        ("GET", "/funders/1/", handle_funder_retrieve),
    )
