"""Tests for VolumesResource using fixtures modeled on staging responses."""

from __future__ import annotations

import json

import httpx

from databrarypy.client import DatabraryClient

from ..fixtures.client import build_client_transport
from ..fixtures.constants import (
    TEST_BASE_URL,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)
from ..fixtures.data_constants import (
    TASK_STATUS_PROCESSING,
    VOLUME_COLLABORATOR_ID_1,
    VOLUME_ID_PRIMARY,
)
from ..fixtures.volume import (
    MOCK_VOLUME_DETAILED,
    build_volumes_transport,
    handle_volume_history,
)
from ..fixtures.volume_collaborators import (
    MOCK_COLLABORATORS_1,
    handle_volume_collaborator_1,
    handle_volume_collaborators_1,
)
from ..fixtures.volume_tags_links_fundings import (
    MOCK_VOLUME_LINKS_1,
    MOCK_VOLUME_TAGS_1,
    handle_volume_fundings_1,
    handle_volume_links_1,
    handle_volume_tags_1,
)


def build_transport():
    client_transport = build_client_transport()
    volumes_transport = build_volumes_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        # Route auth endpoints
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        # Route volume endpoints
        if key in {("GET", "/volumes/"), ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/")}:
            return volumes_transport.handle_request(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/history/"):
            return handle_volume_history(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/download-link/"):
            return volumes_transport.handle_request(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/csv-download-link/"):
            return volumes_transport.handle_request(request)
        # Route other volume endpoints manually
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/tags/"):
            return handle_volume_tags_1(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/links/"):
            return handle_volume_links_1(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/fundings/"):
            return handle_volume_fundings_1(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/collaborators/"):
            return handle_volume_collaborators_1(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/collaborators/1/"):
            return handle_volume_collaborator_1(request)
        return httpx.Response(404, json={"detail": "Not found"})

    return httpx.MockTransport(router)


def test_volumes_read_endpoints() -> None:
    transport = build_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    # list
    page = client.volumes.page(page=1, page_size=10)
    assert page.count == 208
    assert page.results and page.results[0].id == 1

    # retrieve
    detail = client.volumes.retrieve(VOLUME_ID_PRIMARY)
    assert detail.id == VOLUME_ID_PRIMARY
    assert detail.sharing_level == MOCK_VOLUME_DETAILED["sharing_level"]
    assert detail.coauthors and detail.coauthors[0].user is not None

    # tags
    tags = client.volumes.tags(VOLUME_ID_PRIMARY)
    assert tags == MOCK_VOLUME_TAGS_1

    # links
    links = client.volumes.links(VOLUME_ID_PRIMARY)
    assert links and links[0].url == MOCK_VOLUME_LINKS_1[0]["url"]

    # fundings
    fundings = client.volumes.fundings(VOLUME_ID_PRIMARY)
    assert fundings and fundings[0].funder.is_approved is True

    # collaborators
    collabs = client.volumes.collaborators(VOLUME_ID_PRIMARY)
    assert collabs and collabs[0].access_level == MOCK_COLLABORATORS_1[0]["access_level"]

    c0 = client.volumes.collaborator(VOLUME_ID_PRIMARY, collabs[0].id)
    assert c0.id == VOLUME_COLLABORATOR_ID_1
    assert c0.user.id == collabs[0].user.id

    # activity/history
    hist = client.volumes.activity_page(1)
    assert hist.count >= 1 and hist.results[0].timestamp

    # download tasks
    zip_task = client.volumes.request_zip_download(VOLUME_ID_PRIMARY)
    assert zip_task.status == TASK_STATUS_PROCESSING and zip_task.task_id
    csv_task = client.volumes.request_csv_download(VOLUME_ID_PRIMARY)
    assert csv_task.status == TASK_STATUS_PROCESSING and csv_task.task_id


def test_volumes_list_iterators() -> None:
    transport = build_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    # iterate list variant
    list_results = list(client.volumes.list(page=1, page_size=2))
    assert list_results and list_results[0].id == 1
    # activity list variant
    activity_results = list(client.volumes.activity_list(1))
    assert activity_results and activity_results[0].timestamp


# ------------------------------------------------------------------
# Volume categories (enable / disable)
# ------------------------------------------------------------------

_CATEGORIES_PATH = f"/volumes/{VOLUME_ID_PRIMARY}/categories/"


def _build_categories_transport():
    """Transport that handles GET volume detail and POST categories."""
    client_transport = build_client_transport()
    volumes_transport = build_volumes_transport()

    posted_ids: list[list[int]] = []

    def handle_set_categories(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        posted_ids.append(body)
        return httpx.Response(200, json={})

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        if key == ("GET", f"/volumes/{VOLUME_ID_PRIMARY}/"):
            return volumes_transport.handle_request(request)
        if key == ("POST", _CATEGORIES_PATH):
            return handle_set_categories(request)
        return httpx.Response(404, json={"detail": "Not found"})

    return httpx.MockTransport(router), posted_ids


def _make_categories_client(transport):
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()
    return client


def test_get_enabled_categories() -> None:
    transport, _ = _build_categories_transport()
    client = _make_categories_client(transport)

    cats = client.volumes.get_enabled_categories(VOLUME_ID_PRIMARY)
    assert isinstance(cats, list)
    assert len(cats) >= 1
    assert cats[0].id == MOCK_VOLUME_DETAILED["enabled_categories"][0]["id"]
    assert cats[0].name == "context"


def test_set_enabled_categories() -> None:
    transport, posted_ids = _build_categories_transport()
    client = _make_categories_client(transport)

    client.volumes.set_enabled_categories(VOLUME_ID_PRIMARY, [1, 6])
    assert posted_ids == [[1, 6]]


def test_enable_category_adds_new() -> None:
    transport, posted_ids = _build_categories_transport()
    client = _make_categories_client(transport)

    # Volume already has category 7 (context) enabled.
    # Enabling category 1 should POST [7, 1].
    client.volumes.enable_category(VOLUME_ID_PRIMARY, 1)
    assert len(posted_ids) == 1
    assert 7 in posted_ids[0]
    assert 1 in posted_ids[0]


def test_enable_category_noop_if_already_enabled() -> None:
    transport, posted_ids = _build_categories_transport()
    client = _make_categories_client(transport)

    # Category 7 is already enabled; should be a no-op.
    client.volumes.enable_category(VOLUME_ID_PRIMARY, 7)
    assert posted_ids == []


def test_disable_category_removes() -> None:
    transport, posted_ids = _build_categories_transport()
    client = _make_categories_client(transport)

    # Category 7 is enabled; disabling it should POST [].
    client.volumes.disable_category(VOLUME_ID_PRIMARY, 7)
    assert len(posted_ids) == 1
    assert 7 not in posted_ids[0]


def test_disable_category_noop_if_not_enabled() -> None:
    transport, posted_ids = _build_categories_transport()
    client = _make_categories_client(transport)

    # Category 99 is not enabled; should be a no-op.
    client.volumes.disable_category(VOLUME_ID_PRIMARY, 99)
    assert posted_ids == []
