"""RecordsResource tests (list and retrieve)."""

from __future__ import annotations

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import VOLUME_ID_PRIMARY
from tests.fixtures.records import RECORD_ID_1, build_composite_transport


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
    page = client.records.list(VOLUME_ID_PRIMARY, category_id=10, page=1, page_size=10)
    assert page.count == 1
    assert page.results and page.results[0].id == RECORD_ID_1
    assert page.results[0].age and page.results[0].age.total_days == 1972

    # retrieve
    detail = client.records.retrieve(VOLUME_ID_PRIMARY, RECORD_ID_1)
    assert detail.id == RECORD_ID_1
    assert detail.measures["height_cm"] == 120
