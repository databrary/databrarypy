"""Records fixtures and mock handlers."""

from __future__ import annotations

import httpx

from .client import build_client_transport
from .common import build_transport
from .data_constants import VOLUME_ID_PRIMARY
from .factory import make_page

# ---- IDs ----
RECORD_ID_1 = 501


def _get_mock_record_1():
    return {
        "id": RECORD_ID_1,
        "volume": VOLUME_ID_PRIMARY,
        "category_id": 10,
        "measures": {"height_cm": 120, "weight_kg": 25.5},
        "birthday": "2020-01-01",
        "age": {"years": 5, "months": 4, "days": 12, "total_days": 1972},
    }


# ---- Paged payloads ----
def _get_mock_records_page():
    return make_page(results=[_get_mock_record_1()], count=1)


# ---- Handlers ----
def handle_records_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_records_page())


def handle_record_detail(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_record_1())


def build_records_transport():
    return build_transport(
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/records/", handle_records_list),
        ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/records/{RECORD_ID_1}/", handle_record_detail),
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
