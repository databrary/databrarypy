from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def _first_volume_id(client: DatabraryClient) -> int | None:
    vols = client.volumes.page(page=1)
    return _first_id(vols)


def test_sessions_list_and_retrieve(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.sessions.page(vid, page=1)
    assert page.count >= 0
    sid = _first_id(page)
    if sid is not None:
        sess = client.sessions.retrieve(vid, sid)
        assert sess.id == sid


def test_sessions_files(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.sessions.page(vid, page=1)
    if not page.results:
        return
    sid = page.results[0].id

    files = client.sessions.files_page(vid, sid, page=1)
    assert files.count >= 0


def test_sessions_iterators(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.sessions.page(vid, page=1)
    if not page.results:
        return
    sid = page.results[0].id
    seen = []
    for idx, f in enumerate(client.sessions.files_list(vid, sid, page=1, page_size=5)):
        seen.append(f)
        if idx > 5:
            break
    assert isinstance(seen, list)


def test_sessions_list_iterator(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    seen = []
    for idx, s in enumerate(client.sessions.list(vid, page=1, page_size=5)):
        seen.append(s)
        if idx > 5:
            break
    assert isinstance(seen, list)


def test_sessions_get_single_file(client: DatabraryClient):
    vid = _first_volume_id(client)
    if vid is None:
        return
    page = client.sessions.page(vid, page=1)
    if not page.results:
        return
    sid = page.results[0].id
    files = client.sessions.files_page(vid, sid, page=1)
    if not files.results:
        return
    fid = files.results[0].id
    f = client.sessions.get_file(vid, sid, fid)
    assert f.id == fid
