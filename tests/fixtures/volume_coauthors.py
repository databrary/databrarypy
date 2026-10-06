"""Volume coauthor fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .common import build_transport
from .data_constants import VOLUME_COAUTHOR_ID_1, VOLUME_ID_PRIMARY
from .factory import make_page
from .users import MOCK_USER_COAUTHOR

# ---- Volume coauthor objects ----
MOCK_VOLUME_COAUTHOR_1 = {
    "id": VOLUME_COAUTHOR_ID_1,
    "user": MOCK_USER_COAUTHOR,
    "sort_order": 1,
    "volume": VOLUME_ID_PRIMARY,
    "created_at": "2025-03-05T16:35:51.339059Z",
    "updated_at": "2025-03-05T16:35:51.339069Z",
}

MOCK_VOLUME_COAUTHORS_LIST = [MOCK_VOLUME_COAUTHOR_1]

# ---- Paged payloads ----
MOCK_VOLUME_COAUTHORS_PAGE = make_page(
    results=MOCK_VOLUME_COAUTHORS_LIST,
    total_pages=1,
    current_page=1,
    sort_by=None,
    sort_order="asc",
)


def handle_volume_coauthors_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_VOLUME_COAUTHORS_PAGE)


def handle_volume_coauthor_retrieve(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_VOLUME_COAUTHOR_1)


def build_volume_coauthors_transport():
    return build_transport(
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/coauthors/",
            handle_volume_coauthors_list,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/coauthors/{VOLUME_COAUTHOR_ID_1}/",
            handle_volume_coauthor_retrieve,
        ),
    )
