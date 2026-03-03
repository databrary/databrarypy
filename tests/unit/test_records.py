"""RecordsResource tests (read, create, update, delete, measures, assignments)."""

from __future__ import annotations

import httpx
import pytest

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import VOLUME_ID_PRIMARY
from tests.fixtures.records import (
    FILE_ID_1,
    METRIC_ID_NAME,
    METRIC_ID_OPTIONAL,
    RECORD_1_AGE,
    RECORD_1_MEASURES,
    RECORD_CATEGORY_ID_1,
    RECORD_ID_1,
    RECORD_ID_CREATED,
    SESSION_ID_1,
    _get_mock_volume_detail,
    build_composite_transport,
)


def _make_client() -> DatabraryClient:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()
    return client


# ------------------------------------------------------------------
# Read
# ------------------------------------------------------------------


def test_records_list_and_retrieve() -> None:
    client = _make_client()

    page = client.records.page(
        VOLUME_ID_PRIMARY,
        category_id=RECORD_CATEGORY_ID_1,
        page=1,
        page_size=10,
    )
    assert page.count == 1
    assert page.results and page.results[0].id == RECORD_ID_1
    assert page.results[0].age and page.results[0].age.total_days == RECORD_1_AGE["total_days"]

    detail = client.records.retrieve(VOLUME_ID_PRIMARY, RECORD_ID_1)
    assert detail.id == RECORD_ID_1
    assert detail.measures == RECORD_1_MEASURES


def test_records_list_iterator() -> None:
    client = _make_client()

    first_record = next(client.records.list(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1))
    assert first_record.id == RECORD_ID_1


# ------------------------------------------------------------------
# Create
# ------------------------------------------------------------------


def test_records_create() -> None:
    client = _make_client()

    record = client.records.create(
        VOLUME_ID_PRIMARY,
        category_id=RECORD_CATEGORY_ID_1,
        name="New Record",
    )
    assert record.id == RECORD_ID_CREATED
    assert record.volume == VOLUME_ID_PRIMARY
    assert record.category_id == RECORD_CATEGORY_ID_1
    assert str(METRIC_ID_NAME) in record.measures


def test_records_create_with_measures() -> None:
    client = _make_client()

    record = client.records.create(
        VOLUME_ID_PRIMARY,
        category_id=RECORD_CATEGORY_ID_1,
        name="New Record",
        measures={str(METRIC_ID_OPTIONAL): "extra"},
    )
    assert record.id == RECORD_ID_CREATED


def test_records_create_raises_on_bad_volume() -> None:
    """create raises NotFoundError when volume doesn't exist."""
    from databrarypy.errors import NotFoundError

    client = _make_client()

    with pytest.raises(NotFoundError):
        client.records.create(
            999999,
            category_id=RECORD_CATEGORY_ID_1,
            name="Nope",
        )


# ------------------------------------------------------------------
# Update
# ------------------------------------------------------------------


def test_records_update() -> None:
    client = _make_client()

    updated = client.records.update(
        VOLUME_ID_PRIMARY,
        RECORD_ID_1,
        measures={"gender": "Female"},
    )
    assert updated.id == RECORD_ID_1
    assert "gender" in updated.measures


def test_records_update_requires_fields() -> None:
    client = _make_client()

    with pytest.raises(ValueError, match="At least one"):
        client.records.update(VOLUME_ID_PRIMARY, RECORD_ID_1)


# ------------------------------------------------------------------
# Delete
# ------------------------------------------------------------------


def test_records_delete() -> None:
    client = _make_client()

    result = client.records.delete(VOLUME_ID_PRIMARY, RECORD_ID_1)
    assert result is True


# ------------------------------------------------------------------
# Measures
# ------------------------------------------------------------------


def test_records_set_measure() -> None:
    client = _make_client()

    data = client.records.set_measure(
        VOLUME_ID_PRIMARY,
        RECORD_ID_1,
        METRIC_ID_OPTIONAL,
        value="some value",
    )
    assert data.get("value") == "some value"


def test_records_set_measure_date() -> None:
    client = _make_client()

    date_val = {
        "year": 2020,
        "month": 3,
        "day": 15,
        "is_estimated": False,
    }
    data = client.records.set_measure(
        VOLUME_ID_PRIMARY,
        RECORD_ID_1,
        METRIC_ID_OPTIONAL,
        value=date_val,
    )
    assert data.get("year") == 2020


def test_records_delete_measure() -> None:
    client = _make_client()

    result = client.records.delete_measure(VOLUME_ID_PRIMARY, RECORD_ID_1, METRIC_ID_OPTIONAL)
    assert result is True


# ------------------------------------------------------------------
# Record-file associations
# ------------------------------------------------------------------


def test_assign_record_to_file() -> None:
    client = _make_client()

    result = client.sessions.assign_record_to_file(
        VOLUME_ID_PRIMARY, SESSION_ID_1, FILE_ID_1, RECORD_ID_1
    )
    assert result["record_id"] == RECORD_ID_1
    assert result["status"] == "assigned"


def test_assign_record_to_file_warns_on_duplicate(caplog) -> None:
    """When the server returns 200 (already assigned), a warning is logged."""
    import logging

    from tests.fixtures.records import _ASSIGN_PATH

    call_count = 0

    def _router(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        if request.method == "POST" and request.url.path == "/o/token/":
            return httpx.Response(
                200,
                json={
                    "access_token": "tok",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
        if request.method == "POST" and request.url.path == _ASSIGN_PATH:
            call_count += 1
            if call_count == 1:
                return httpx.Response(201, json={"record_id": RECORD_ID_1, "status": "assigned"})
            return httpx.Response(200, json={"record_id": RECORD_ID_1, "status": "assigned"})
        return httpx.Response(404)

    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="u@e.org",
        password="pw",
        transport=httpx.MockTransport(_router),
    )
    client.auth.login()

    with caplog.at_level(logging.WARNING, logger="databrarypy.resources.sessions"):
        client.sessions.assign_record_to_file(
            VOLUME_ID_PRIMARY, SESSION_ID_1, FILE_ID_1, RECORD_ID_1
        )
    assert "already assigned" not in caplog.text

    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="databrarypy.resources.sessions"):
        client.sessions.assign_record_to_file(
            VOLUME_ID_PRIMARY, SESSION_ID_1, FILE_ID_1, RECORD_ID_1
        )
    assert "already assigned" in caplog.text


def test_unassign_record_from_file() -> None:
    client = _make_client()

    result = client.sessions.unassign_record_from_file(
        VOLUME_ID_PRIMARY, SESSION_ID_1, FILE_ID_1, RECORD_ID_1
    )
    assert result["record_id"] == RECORD_ID_1
    assert result["status"] == "unassigned"


# ------------------------------------------------------------------
# _get_priority_metric_id edge cases
# ------------------------------------------------------------------


def _client_with_volume(volume_payload: dict) -> DatabraryClient:
    """Build a client whose GET /volumes/1/ returns *volume_payload*."""
    from tests.fixtures.records import (
        _get_mock_created_record,
        handle_records_list,
    )

    def _router(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/o/token/":
            return httpx.Response(
                200,
                json={
                    "access_token": "tok",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
        if request.url.path == f"/volumes/{VOLUME_ID_PRIMARY}/":
            return httpx.Response(200, json=volume_payload)
        if request.method == "GET" and request.url.path == f"/volumes/{VOLUME_ID_PRIMARY}/records/":
            return handle_records_list(request)
        if (
            request.method == "POST"
            and request.url.path == f"/volumes/{VOLUME_ID_PRIMARY}/records/"
        ):
            return httpx.Response(201, json=_get_mock_created_record())
        return httpx.Response(404)

    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="u@e.org",
        password="pw",
        transport=httpx.MockTransport(_router),
    )
    client.auth.login()
    return client


def test_priority_metric_no_enabled_categories() -> None:
    vol = _get_mock_volume_detail()
    vol["enabled_categories"] = []
    client = _client_with_volume(vol)
    with pytest.raises(ValueError, match="Cannot resolve"):
        client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="X")


def test_priority_metric_no_enabled_metrics() -> None:
    vol = _get_mock_volume_detail()
    vol["enabled_metrics"] = []
    client = _client_with_volume(vol)
    with pytest.raises(ValueError, match="Cannot resolve"):
        client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="X")


def test_priority_metric_category_not_found() -> None:
    vol = _get_mock_volume_detail()
    client = _client_with_volume(vol)
    with pytest.raises(ValueError, match="Cannot resolve"):
        client.records.create(VOLUME_ID_PRIMARY, category_id=9999, name="X")


def test_priority_metric_empty_category_metrics() -> None:
    vol = _get_mock_volume_detail()
    vol["enabled_categories"][0]["metrics"] = []
    client = _client_with_volume(vol)
    with pytest.raises(ValueError, match="Cannot resolve"):
        client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="X")


def test_priority_metric_no_enabled_overlap() -> None:
    """Category has metrics but none are in the volume's enabled list."""
    vol = _get_mock_volume_detail()
    vol["enabled_metrics"] = [{"id": 9999, "name": "other", "type": "string"}]
    client = _client_with_volume(vol)
    with pytest.raises(ValueError, match="Cannot resolve"):
        client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="X")


def test_priority_metric_fallback_to_name_priority() -> None:
    """No required metric; falls back to name-priority lookup."""
    vol = _get_mock_volume_detail()
    for m in vol["enabled_categories"][0]["metrics"]:
        m["required"] = False
    client = _client_with_volume(vol)
    record = client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="Y")
    assert str(METRIC_ID_NAME) in record.measures


def test_priority_metric_fallback_to_first_available() -> None:
    """No required, no name/id/description match; falls back to first."""
    vol = _get_mock_volume_detail()
    for m in vol["enabled_categories"][0]["metrics"]:
        m["required"] = False
        m["name"] = "custom_metric"
    client = _client_with_volume(vol)
    record = client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="Z")
    assert record.id == RECORD_ID_CREATED


def test_priority_metric_non_dict_volume_response() -> None:
    """Volume endpoint returns a non-dict (e.g. empty list)."""

    def _router(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/o/token/":
            return httpx.Response(
                200,
                json={
                    "access_token": "tok",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
        if request.url.path == f"/volumes/{VOLUME_ID_PRIMARY}/":
            return httpx.Response(200, json=[])
        return httpx.Response(404)

    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="u@e.org",
        password="pw",
        transport=httpx.MockTransport(_router),
    )
    client.auth.login()
    with pytest.raises(ValueError, match="Cannot resolve"):
        client.records.create(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, name="X")


# ------------------------------------------------------------------
# create / update with participant
# ------------------------------------------------------------------


def test_records_create_with_participant() -> None:
    client = _make_client()
    record = client.records.create(
        VOLUME_ID_PRIMARY,
        category_id=RECORD_CATEGORY_ID_1,
        name="Participant rec",
        participant={"birthday": {"year": 2020, "month": 1, "day": 15}},
    )
    assert record.id == RECORD_ID_CREATED


def test_records_update_with_participant() -> None:
    client = _make_client()
    updated = client.records.update(
        VOLUME_ID_PRIMARY,
        RECORD_ID_1,
        participant={"birthday": {"year": 2021, "month": 6, "day": 1}},
    )
    assert updated.id == RECORD_ID_1


# ------------------------------------------------------------------
# _post_json / _patch_json empty-body fallback
# ------------------------------------------------------------------


def test_post_json_empty_body_returns_empty_dict() -> None:
    """POST returning 204 No Content falls back to {}."""

    def _router(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/o/token/":
            return httpx.Response(
                200,
                json={
                    "access_token": "tok",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
        if request.method == "POST" and request.url.path == "/empty/":
            return httpx.Response(204)
        return httpx.Response(404)

    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="u@e.org",
        password="pw",
        transport=httpx.MockTransport(_router),
    )
    client.auth.login()
    result = client.records._post_json("/empty/", json={})
    assert result == {}


def test_patch_json_empty_body_returns_empty_dict() -> None:
    """PATCH returning 204 No Content falls back to {}."""

    def _router(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/o/token/":
            return httpx.Response(
                200,
                json={
                    "access_token": "tok",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
        if request.method == "PATCH" and request.url.path == "/empty/":
            return httpx.Response(204)
        return httpx.Response(404)

    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="u@e.org",
        password="pw",
        transport=httpx.MockTransport(_router),
    )
    client.auth.login()
    result = client.records._patch_json("/empty/", json={})
    assert result == {}
