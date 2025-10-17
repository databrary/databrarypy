from __future__ import annotations

from databrarypy.client import DatabraryClient


def _first_id(page) -> int | None:
    if page.results:
        item = page.results[0]
        return getattr(item, "id", None)
    return None


def test_users_list_and_retrieve(client: DatabraryClient):
    page = client.users.page(page=1)
    assert page.count >= 0
    uid = _first_id(page)
    if uid is not None:
        user = client.users.retrieve(uid)
        assert user.id == uid


def test_users_self(client: DatabraryClient):
    who = client.whoami()
    email = who.user
    assert email
    # Find user by email from the first page(s)
    page = client.users.page(search=email, page=1)
    assert page.count >= 0
    # If direct search didn't resolve id, fall back to first result match
    uid = None
    for u in page.results:
        if getattr(u, "email", None) == email:
            uid = u.id
            break
    if uid is None and page.results:
        uid = page.results[0].id
    assert uid is not None
    me = client.users.retrieve(uid, for_self=True)
    assert me.email == email


def test_users_sponsorships_and_affiliates(client: DatabraryClient):
    who = client.whoami()
    email = who.user
    assert email
    page = client.users.page(search=email, page=1)
    uid = None
    for u in page.results:
        if getattr(u, "email", None) == email:
            uid = u.id
            break
    if uid is None and page.results:
        uid = page.results[0].id
    assert uid is not None
    sponsor_list = client.users.sponsors(uid)
    assert isinstance(sponsor_list, list)

    affiliates = client.users.affiliates(uid)
    assert isinstance(affiliates, list)


def test_users_activity_iterators(client: DatabraryClient):
    who = client.whoami()
    email = who.user
    assert email
    page = client.users.page(search=email, page=1)
    uid = None
    for u in page.results:
        if getattr(u, "email", None) == email:
            uid = u.id
            break
    if uid is None and page.results:
        uid = page.results[0].id
    assert uid is not None

    act_page = client.users.activity_page(uid, page=1)
    assert act_page.count >= 0
    # Iterator variant
    seen = []
    for idx, item in enumerate(client.users.activity_list(uid, page=1, page_size=5)):
        seen.append(item)
        if idx > 5:
            break
    assert isinstance(seen, list)


def test_users_volumes_and_avatar(client: DatabraryClient):
    who = client.whoami()
    uid: int | None = None
    if isinstance(who, dict):
        uid = who.get("id")
    if uid is None:
        page = client.users.page(page=1)
        if page.results:
            uid = page.results[0].id
    if uid is None:
        return

    volumes = client.users.volumes_page(uid, page=1)
    assert volumes.count >= 0

    # Avatar can be empty bytes if 404; call to ensure path works
    data = client.users.avatar(uid)
    assert isinstance(data, (bytes, str))


def test_users_volumes_list_iterator(client: DatabraryClient):
    who = client.whoami()
    uid: int | None = None
    if isinstance(who, dict):
        uid = who.get("id")
    if uid is None:
        page = client.users.page(page=1)
        if page.results:
            uid = page.results[0].id
    if uid is None:
        return
    seen = []
    for idx, v in enumerate(client.users.volumes_list(uid, page=1, page_size=5)):
        seen.append(v)
        if idx > 5:
            break
    assert isinstance(seen, list)
