"""Tests for CategoriesResource."""

from databrarypy.client import DatabraryClient

from ..fixtures.categories import _get_mock_category, build_composite_transport
from ..fixtures.constants import (
    TEST_BASE_URL,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)


def test_categories_list_and_retrieve():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    items = client.categories.list()
    assert len(items) == 1
    cat = items[0]
    expected = _get_mock_category()
    assert cat.name == expected["name"]
    assert len(cat.metrics) == len(expected["metrics"])

    detail = client.categories.retrieve(cat.id)
    assert detail.id == cat.id
    assert any(m.name == expected["metrics"][0]["name"] for m in detail.metrics)
