"""UsersResource tests."""

import pytest

from databrarypy.client import DatabraryClient
from databrarypy.errors import NotFoundError
from tests.fixtures.data_constants import (
    USER_ID_1,
    USER_ID_2,
    USER_ID_NOT_FOUND,
    USER_ID_PRIMARY,
)
from tests.fixtures.users import (
    MOCK_USER_1,
    MOCK_USER_6_AFFILIATE_ACTIVE,
    MOCK_USER_STATISTICS,
    build_composite_transport,
)


def _make_client():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()
    return client


def test_users_list_and_retrieve():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()

    page = client.users.page(search="alex")
    assert page.count == 1

    assert page.results[0].first_name == MOCK_USER_1["first_name"]

    me = client.users.retrieve(6, for_self=True)
    assert me.has_api_access is True
    assert me.is_authorized_investigator is True

    sponsors = client.users.sponsors(6)
    assert sponsors and sponsors[0].id == 101
    vols = client.users.volumes_page(6)
    assert vols.count == 0
    assert vols.results == []
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
        transport=transport,
    )
    client.auth.login()

    # Exercise include_expired parameter
    affiliates = client.users.affiliates(6, include_expired=True)
    assert affiliates and len(affiliates) >= 1
    assert affiliates[0].id == MOCK_USER_6_AFFILIATE_ACTIVE["id"]


def test_users_list_with_filters_and_volumes():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()

    page = client.users.page(
        search="john",
        include_suspended=True,
        exclude_self=True,
        is_authorized_investigator=True,
        has_api_access=False,
    )
    assert page.count >= 0

    vols = client.users.volumes_page(7)
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
        transport=transport,
    )
    client.auth.login()

    page = client.users.activity_page(USER_ID_PRIMARY, page=1, page_size=5)
    assert page.count >= 1
    item = page.results[0]
    # ActivityItem allows extras; only assert required fields
    assert item.type and item.timestamp


def test_users_iterators():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    client.auth.login()

    first_user = next(client.users.list(search="alex"))
    assert first_user.id is not None
    # Iterate generators to cover code paths
    vols = list(client.users.volumes_list(6))
    assert vols == []

    acts = list(client.users.activity_list(6))
    assert acts and all(item.timestamp for item in acts)


def test_user_statistics_ok():
    client = _make_client()

    stats = client.users.statistics(USER_ID_1)

    assert stats is not None
    assert stats.user_id == USER_ID_1
    assert stats.volumes_number == MOCK_USER_STATISTICS["volumes_number"]
    assert stats.files_number == MOCK_USER_STATISTICS["files_number"]
    assert stats.uploaded_data_footprint == MOCK_USER_STATISTICS["uploaded_data_footprint"]


def test_user_statistics_no_content():
    client = _make_client()

    stats = client.users.statistics(USER_ID_2)

    assert stats is None


def test_user_statistics_not_found():
    client = _make_client()

    with pytest.raises(NotFoundError):
        client.users.statistics(USER_ID_NOT_FOUND)
