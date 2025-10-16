"""Tests for VolumesResource using fixtures modeled on staging responses."""

from __future__ import annotations

import httpx

from databrarypy.client import DatabraryClient

from ..fixtures.client import build_client_transport
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
        base_url="https://example.org",
        client_id="id",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="tests",
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
        base_url="https://example.org",
        client_id="id",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="tests",
        transport=transport,
    )
    client.auth.login()

    # iterate list variant
    _ = list(client.volumes.list(page=1, page_size=2))
    # activity list variant
    _ = list(client.volumes.activity_list(1))
