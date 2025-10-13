"""UsersResource tests."""

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import USER_ID_PRIMARY
from tests.fixtures.users import build_composite_transport


def test_users_list_and_retrieve():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    page = client.users.list(search="alex")
    assert page.count == 1
    assert page.results[0].first_name == "Alex"

    me = client.users.retrieve(6, for_self=True)
    assert me.has_api_access is True
    assert me.is_authorized_investigator is True

    sponsors = client.users.sponsors(6)
    assert sponsors and sponsors[0].id == 101
    vols = client.users.volumes(6)
    assert vols.count == 0 and vols.results == []
    avatar2 = client.users.avatar(6)
    assert avatar2.startswith(b"\x89PNG")
    # save avatar to dir and to explicit file
    from pathlib import Path

    out_dir = Path(".pytest_tmp/user_avatar")
    if out_dir.exists() and out_dir.is_file():
        out_dir.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)
    saved_path = client.users.avatar(6, dest_path=str(out_dir))
    assert saved_path
    explicit_file = out_dir / "avatar.png"
    saved_path2 = client.users.avatar(6, dest_path=str(explicit_file))
    assert saved_path2.endswith("avatar.png")

    # Cover public branch of retrieve (for_self=False)
    public = client.users.retrieve(6)
    assert public.id == me.id


def test_users_affiliates_with_params():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    # Exercise include_expired, page, page_size path
    page = client.users.affiliates(6, include_expired=True, page=1, page_size=10)
    assert page.count >= 0


def test_users_list_with_filters_and_volumes():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    page = client.users.list(
        search="john",
        include_suspended=True,
        exclude_self=True,
        is_authorized_investigator=True,
        has_api_access=False,
    )
    assert page.count >= 0

    vols = client.users.volumes(7)
    assert vols.count == 2
    assert [v.title for v in vols.results] == ["Vol1", "Vol2"]


def test_users_activity_list():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    page = client.users.activity(USER_ID_PRIMARY, page=1, page_size=5)
    assert page.count >= 1
    item = page.results[0]
    # ActivityItem allows extras; only assert required fields
    assert item.type and item.timestamp
