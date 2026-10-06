"""Records fixtures and mock handlers."""

from __future__ import annotations

import json

import httpx

from .client import build_client_transport
from .common import build_transport
from .data_constants import VOLUME_ID_PRIMARY
from .factory import make_page

# ---- IDs ----
RECORD_ID_1 = 501
RECORD_ID_CREATED = 502
RECORD_CATEGORY_ID_1 = 10
RECORD_1_AGE = {"years": 5, "months": 4, "days": 12, "total_days": 1972}
RECORD_1_MEASURES = {"height_cm": 120, "weight_kg": 25.5}

METRIC_ID_NAME = 50
METRIC_ID_OPTIONAL = 51
SESSION_ID_1 = 100
FILE_ID_1 = 200


def _get_mock_record_1():
    return {
        "id": RECORD_ID_1,
        "volume": VOLUME_ID_PRIMARY,
        "category_id": RECORD_CATEGORY_ID_1,
        "measures": RECORD_1_MEASURES,
        "birthday": "2020-01-01",
        "age": RECORD_1_AGE,
    }


def _get_mock_created_record():
    return {
        "id": RECORD_ID_CREATED,
        "volume": VOLUME_ID_PRIMARY,
        "category_id": RECORD_CATEGORY_ID_1,
        "measures": {str(METRIC_ID_NAME): "New Record"},
        "birthday": None,
        "age": None,
    }


def _get_mock_volume_detail():
    """Minimal volume detail with enabled categories/metrics for name-metric resolution."""
    return {
        "id": VOLUME_ID_PRIMARY,
        "title": "Test Volume",
        "description": None,
        "short_name": None,
        "sharing_level": "private",
        "coauthors": [],
        "owner_institution": {
            "id": 1,
            "name": "Test Inst",
            "url": None,
            "is_active": True,
        },
        "enabled_categories": [
            {
                "id": RECORD_CATEGORY_ID_1,
                "name": "task",
                "description": None,
                "metrics": [
                    {
                        "id": METRIC_ID_NAME,
                        "name": "name",
                        "release": None,
                        "type": "string",
                        "options": None,
                        "assumed": None,
                        "description": None,
                        "required": True,
                    },
                    {
                        "id": METRIC_ID_OPTIONAL,
                        "name": "description",
                        "release": None,
                        "type": "string",
                        "options": None,
                        "assumed": None,
                        "description": None,
                        "required": False,
                    },
                ],
            }
        ],
        "enabled_metrics": [
            {"id": METRIC_ID_NAME, "name": "name", "type": "string"},
            {"id": METRIC_ID_OPTIONAL, "name": "description", "type": "string"},
        ],
        "fundings": [],
        "links": [],
        "access_level": "admin",
        "has_admin_access": True,
        "citation": None,
        "doi": None,
        "session_count": 0,
        "session_count_shared": 0,
        "participant_count": 0,
        "participant_gender_counts": None,
        "file_counts": None,
        "file_sizes": None,
        "linked_file_counts": None,
        "linked_file_sizes": None,
        "thumbnail": None,
    }


# ---- Paged payloads ----
def _get_mock_records_page():
    return make_page(results=[_get_mock_record_1()], count=1)


# ---- Handlers ----
def handle_records_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_records_page())


def handle_record_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_record_1())


def handle_volume_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_volume_detail())


def handle_record_create(request: httpx.Request) -> httpx.Response:
    return httpx.Response(201, json=_get_mock_created_record())


def handle_record_update(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    record = _get_mock_record_1()
    if "measures" in body:
        record["measures"] = {**record["measures"], **body["measures"]}
    return httpx.Response(200, json=record)


def handle_record_delete(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def handle_set_measure(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    return httpx.Response(200, json=body)


def handle_delete_measure(request: httpx.Request) -> httpx.Response:
    return httpx.Response(204)


def handle_assign_record(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    return httpx.Response(200, json={"record_id": body["record_id"], "status": "assigned"})


def handle_unassign_record(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    return httpx.Response(200, json={"record_id": body["record_id"], "status": "unassigned"})


_MEASURE_PATH = f"/volumes/{VOLUME_ID_PRIMARY}/records/{RECORD_ID_1}/measures/{METRIC_ID_OPTIONAL}/"

_ASSIGN_PATH = (
    f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{FILE_ID_1}/assign-record/"
)

_UNASSIGN_PATH = (
    f"/volumes/{VOLUME_ID_PRIMARY}/sessions/{SESSION_ID_1}/files/{FILE_ID_1}/unassign-record/"
)


def build_records_transport():
    return build_transport(
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/records/", handle_records_list),
        (
            "GET",
            f"/volumes/{VOLUME_ID_PRIMARY}/records/{RECORD_ID_1}/",
            handle_record_detail,
        ),
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/", handle_volume_detail),
        ("POST", f"/volumes/{VOLUME_ID_PRIMARY}/records/", handle_record_create),
        (
            "PATCH",
            f"/volumes/{VOLUME_ID_PRIMARY}/records/{RECORD_ID_1}/",
            handle_record_update,
        ),
        (
            "DELETE",
            f"/volumes/{VOLUME_ID_PRIMARY}/records/{RECORD_ID_1}/",
            handle_record_delete,
        ),
        ("POST", _MEASURE_PATH, handle_set_measure),
        ("DELETE", _MEASURE_PATH, handle_delete_measure),
        ("POST", _ASSIGN_PATH, handle_assign_record),
        ("POST", _UNASSIGN_PATH, handle_unassign_record),
    )


def build_composite_transport():
    client_transport = build_client_transport()
    records_transport = build_records_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        return records_transport.handle_request(request)

    return httpx.MockTransport(router)
