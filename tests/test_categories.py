"""Tests for CategoriesResource."""

from databrarypy.client import DatabraryClient

from .fixtures.categories import build_composite_transport


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
    assert cat.name == "Demographics"
    assert len(cat.metrics) == 2

    detail = client.categories.retrieve(cat.id)
    assert detail.id == cat.id
    assert any(m.name == "age" for m in detail.metrics)
