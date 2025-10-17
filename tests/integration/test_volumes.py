from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def test_volumes_list_and_detail(client: DatabraryClient):
    page = client.volumes.page(page=1)
    assert page.count >= 0
    vid = _first_id(page)
    if vid is not None:
        vol = client.volumes.retrieve(vid)
        assert vol.id == vid


def test_volumes_tags_links_fundings(client: DatabraryClient):
    page = client.volumes.page(page=1)
    if not page.results:
        return
    vid = page.results[0].id
    tags = client.volumes.tags(vid)
    assert isinstance(tags, list)

    links = client.volumes.links(vid)
    assert isinstance(links, list)

    fundings = client.volumes.fundings(vid)
    assert isinstance(fundings, list)


def test_volumes_collaborators(client: DatabraryClient):
    page = client.volumes.page(page=1)
    if not page.results:
        return
    vid = page.results[0].id

    collabs = client.volumes.collaborators(vid)
    assert isinstance(collabs, list)
    if collabs:
        cid = collabs[0].id
        collab = client.volumes.collaborator(vid, cid)
        assert collab.id == cid


def test_volumes_activity(client: DatabraryClient):
    page = client.volumes.page(page=1)
    if not page.results:
        return
    vid = page.results[0].id
    act_page = client.volumes.activity_page(vid, page=1)
    assert act_page.count >= 0

    seen = []
    for idx, item in enumerate(client.volumes.activity_list(vid, page=1, page_size=5)):
        seen.append(item)
        if idx > 5:
            break
    assert isinstance(seen, list)
