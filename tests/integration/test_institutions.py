from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def test_institutions_list_and_retrieve(client: DatabraryClient):
    page = client.institutions.page(page=1)
    assert page.count >= 0
    iid = _first_id(page)
    if iid is not None:
        inst = client.institutions.retrieve(iid)
        assert inst.id == iid


def test_institutions_avatar_and_investigators(client: DatabraryClient):
    page = client.institutions.page(page=1)
    if not page.results:
        return
    iid = page.results[0].id

    # Avatar may be missing; ensure call works
    data = client.institutions.avatar(iid)
    assert isinstance(data, (bytes, str))

    # Investigators derived client-side from affiliates
    investigators = list(client.institutions.authorized_investigators(iid, page=1))
    assert isinstance(investigators, list)
