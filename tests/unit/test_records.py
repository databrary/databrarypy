"""RecordsResource tests (list and retrieve)."""

from __future__ import annotations

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import VOLUME_ID_PRIMARY
from tests.fixtures.records import (
    RECORD_1_AGE,
    RECORD_1_MEASURES,
    RECORD_CATEGORY_ID_1,
    RECORD_ID_1,
    build_composite_transport,
)


def test_records_list_and_retrieve() -> None:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    # list
    page = client.records.page(
        VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1, page=1, page_size=10
    )
    assert page.count == 1
    assert page.results and page.results[0].id == RECORD_ID_1
    assert page.results[0].age and page.results[0].age.total_days == RECORD_1_AGE["total_days"]

    # retrieve
    detail = client.records.retrieve(VOLUME_ID_PRIMARY, RECORD_ID_1)
    assert detail.id == RECORD_ID_1
    assert detail.measures == RECORD_1_MEASURES


def test_records_list_iterator() -> None:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    first_record = next(client.records.list(VOLUME_ID_PRIMARY, category_id=RECORD_CATEGORY_ID_1))
    assert first_record.id == RECORD_ID_1
