from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def test_tags_list_and_retrieve(client: DatabraryClient):
    page = client.tags.list(page=1)
    assert page.count >= 0
    tid = _first_id(page)
    if tid is not None:
        tag = client.tags.retrieve(tid)
        assert tag.id == tid
