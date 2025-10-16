"""Tests for VolumesResource using fixtures modeled on staging responses."""

from __future__ import annotations

import httpx

from databrarypy.client import DatabraryClient

from .fixtures.client import build_client_transport
from .fixtures.data_constants import VOLUME_ID_PRIMARY
from .fixtures.volume import build_volumes_transport
from .fixtures.volume_collaborators import (
    handle_volume_collaborator_1,
    handle_volume_collaborators_1,
)
from .fixtures.volume_tags_links_fundings import (
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
    page = client.volumes.list(page=1, page_size=10)
    assert page.count == 208
    assert page.results and page.results[0].id == 1

    # retrieve
    detail = client.volumes.retrieve(1)
    assert detail.id == 1
    assert detail.sharing_level == "public"
    assert detail.coauthors and detail.coauthors[0].user is not None

    # tags
    tags = client.volumes.tags(1)
    assert isinstance(tags, list) and len(tags) > 0

    # links
    links = client.volumes.links(1)
    assert links and links[0].url.startswith("http")

    # fundings
    fundings = client.volumes.fundings(1)
    assert fundings and fundings[0]["funder"]["is_approved"] is True

    # collaborators
    collabs = client.volumes.collaborators(1)
    assert collabs and collabs[0].access_level in {"investigator", "read only", "read write"}

    c0 = client.volumes.collaborator(1, collabs[0].id)
    assert c0.user.id == collabs[0].user.id
