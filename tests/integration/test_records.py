from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def _first_volume_id(client: DatabraryClient) -> int | None:
    vols = client.volumes.list(page=1)
    return _first_id(vols)


def test_records_list_and_retrieve(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.records.list(vid, page=1)
    assert page.count >= 0
    rid = _first_id(page)
    if rid is not None:
        rec = client.records.retrieve(vid, rid)
        assert rec.id == rid
