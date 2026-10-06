"""Tests for TagsResource."""

from databrarypy.client import DatabraryClient

from ..fixtures.constants import (
    TEST_BASE_URL,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)
from ..fixtures.tags import _get_mock_tag, build_composite_transport


def test_tags_list_and_retrieve():
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

    page = client.tags.page(search="lang", ordering="name")
    assert page.count == 1
    tag = page.results[0]
    expected = _get_mock_tag()
    assert tag.name == expected["name"]

    detail = client.tags.retrieve(tag.id)
    assert detail.id == tag.id


def test_tags_list_iterator():
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

    first_tag = next(client.tags.list(search="video"))
    assert getattr(first_tag, "id", None) is not None
