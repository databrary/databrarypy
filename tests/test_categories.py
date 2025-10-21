"""Tests for CategoriesResource."""

from databrarypy.client import DatabraryClient

from .fixtures.categories import _get_mock_category, build_composite_transport


def test_categories_list_and_retrieve():
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

    page = client.categories.list(page=1, page_size=10, ordering="name")
    assert page.count == 1
    cat = page.results[0]
    expected = _get_mock_category()
    assert cat.name == expected["name"]
    assert len(cat.metrics) == len(expected["metrics"])

    detail = client.categories.retrieve(cat.id)
    assert detail.id == cat.id
    assert any(m.name == expected["metrics"][0]["name"] for m in detail.metrics)
