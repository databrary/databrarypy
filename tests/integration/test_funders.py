from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def test_funders_list_and_retrieve(client: DatabraryClient):
    items = client.funders.list(is_approved=True)
    assert isinstance(items, list)
    fid = items[0].id if items else None
    if fid is not None:
        funder = client.funders.retrieve(fid)
        assert funder.id == fid
