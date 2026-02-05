"""Volume fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .common import build_transport
from .data_constants import TASK_STATUS_PROCESSING, VOLUME_ID_PRIMARY
from .factory import make_page
from .folders import FOLDER_ID_1
from .funders import MOCK_FUNDINGS_LIST
from .institutions import MOCK_INSTITUTION_1_DETAILED
from .sessions import SESSION_ID_1
from .sponsorships import _get_mock_institution_sponsorship_1
from .volume_coauthors import MOCK_VOLUME_COAUTHORS_LIST
from .volume_metrics import MOCK_VOLUME_CATEGORIES, MOCK_VOLUME_CITATION, MOCK_VOLUME_METRICS
from .volume_tags_links_fundings import MOCK_VOLUME_LINKS_1


# ---- Base Volume Object ----
def _get_mock_volume_base():
    """Get mock volume base (lazy to avoid issues with dict copying)."""
    return {
        "id": VOLUME_ID_PRIMARY,
        "title": "Sample Research Dataset Collection",
        "short_name": None,
        "sharing_level": "public",
        "owner_connection": _get_mock_institution_sponsorship_1(),
        "owner_institution": MOCK_INSTITUTION_1_DETAILED,
        "access_level": "superuser",
    }


# ---- Detailed Volume Object (extends base) ----
def _get_mock_volume_detailed():
    """Get mock volume detailed (lazy to avoid issues with dict copying)."""
    return {
        **_get_mock_volume_base(),
        "updated_at": "2025-03-05T16:34:40.872393Z",
        "created_at": "2025-03-05T16:33:56.704147Z",
        "description": "A comprehensive collection of research data and materials for testing purposes.",
        "coauthors": MOCK_VOLUME_COAUTHORS_LIST,
        "fundings": MOCK_FUNDINGS_LIST,
        "links": MOCK_VOLUME_LINKS_1,
        "enabled_categories": MOCK_VOLUME_CATEGORIES,
        "enabled_metrics": MOCK_VOLUME_METRICS,
        "has_admin_access": True,
        "citation": MOCK_VOLUME_CITATION,
        "session_count": 24,
        "session_count_shared": 23,
        "participant_count": 0,
        "participant_gender_counts": {"male": 0, "female": 0, "other": 0},
        "file_counts": {
            "session": {
                "private": 0,
                "authorized_users": 0,
                "learning_audiences": 0,
                "public": 121,
            },
            "folder": {"private": 0, "authorized_users": 0, "learning_audiences": 0, "public": 18},
        },
        "thumbnail": None,
    }


MOCK_VOLUME_DETAILED = _get_mock_volume_detailed()


def _get_mock_volume_history_page():
    items = [
        {
            "type": "volume_change",
            "timestamp": "2025-06-03T09:00:00Z",
            "field": "title",
            "old_value": "Old Title",
            "new_value": "Sample Research Dataset Collection",
        },
        {
            "type": "session_change",
            "timestamp": "2025-06-03T10:00:00Z",
            "session": {"id": SESSION_ID_1, "name": "Session A"},
            "action": "created",
        },
        {
            "type": "folder_change",
            "timestamp": "2025-06-03T11:00:00Z",
            "folder": {"id": FOLDER_ID_1, "name": "Folder A"},
            "action": "updated",
        },
    ]
    return make_page(results=items, count=len(items))


# ---- Paged payloads ----
def _get_mock_volumes_page():
    return make_page(results=[_get_mock_volume_base()], count=208)


MOCK_VOLUMES_PAGE = _get_mock_volumes_page()


# ---- Handler functions ----
def handle_volumes_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_volumes_page())


def handle_volume_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_volume_detailed())


def handle_volume_history(request: httpx.Request) -> httpx.Response:
    assert request.url.path == f"/volumes/{VOLUME_ID_PRIMARY}/history/"
    return httpx.Response(200, json=_get_mock_volume_history_page())


def handle_volume_zip_download_link(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200, json={"status": TASK_STATUS_PROCESSING, "message": None, "task_id": "zip-1"}
    )


def handle_volume_csv_download_link(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200, json={"status": TASK_STATUS_PROCESSING, "message": None, "task_id": "csv-1"}
    )


def build_volumes_transport():
    return build_transport(
        ("GET", "/volumes/", handle_volumes_list),
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/", handle_volume_detail),
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/history/", handle_volume_history),
        # Downloads
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/download-link/",
            handle_volume_zip_download_link,
        ),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/csv-download-link/",
            handle_volume_csv_download_link,
        ),
    )
