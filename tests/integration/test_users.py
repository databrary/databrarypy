from __future__ import annotations

from pathlib import Path

import pytest
from tests.conftest import collect_items, first_list_item, first_page_item

from databrarypy.client import DatabraryClient
from databrarypy.models import UserStatistics


def _resolve_current_user(client: DatabraryClient) -> tuple[str, int | None]:
    """Return (email, user_id) for the authenticated user via search fallback."""

    who = client.whoami()
    email = who.user
    users_iter = client.users.list(search=email, page=1)
    user = next((_user for _user in users_iter if _user.email == email), None)
    return email, user.id if user is not None else None


def test_users_list_and_retrieve(client: DatabraryClient):
    page = client.users.page(page=1)
    assert page.count >= 0
    first_user = first_page_item(page)
    if first_user is None:
        pytest.skip("No users available to test users")
    user = client.users.retrieve(first_user.id)
    assert user.id == first_user.id


def test_users_self(client: DatabraryClient):
    email, uid = _resolve_current_user(client)
    if uid is None:
        pytest.skip("Authenticated user id unavailable in search results")
    me = client.users.retrieve(uid, for_self=True)
    assert me.email == email


def test_users_sponsorships_and_affiliates(client: DatabraryClient):
    _, user_id = _resolve_current_user(client)
    if user_id is None:
        pytest.skip("Authenticated user id unavailable in search results")

    sponsor_list = client.users.sponsors(user_id)
    assert len(sponsor_list) >= 0

    affiliates = client.users.affiliates(user_id)
    assert len(affiliates) >= 0


def test_users_activity_iterators(client: DatabraryClient):
    _, user_id = _resolve_current_user(client)
    if user_id is None:
        pytest.skip("Authenticated user id unavailable in search results")

    act_page = client.users.activity_page(user_id, page=1)
    assert act_page.count >= 0
    # Iterator variant
    seen_items = collect_items(client.users.activity_list(user_id, page=1, page_size=5), limit=6)
    assert len(seen_items) <= 6


def test_users_volumes_and_avatar(client: DatabraryClient):
    _, uid = _resolve_current_user(client)
    if uid is None:
        pytest.skip("Authenticated user id unavailable in search results")

    volumes = client.users.volumes_page(uid, page=1)
    assert volumes.count >= 0
    first_volume = first_list_item(volumes.results)
    if first_volume is None:
        pytest.skip("User volumes endpoint returned no data")
    assert first_volume.title

    # Avatar can be empty bytes if 404; call to ensure path works
    data = client.users.avatar(uid)
    assert isinstance(data, (bytes, str))


def test_users_volumes_list_iterator(client: DatabraryClient):
    _, uid = _resolve_current_user(client)
    if uid is None:
        pytest.skip("Authenticated user id unavailable in search results")
    seen_items = collect_items(client.users.volumes_list(uid, page=1, page_size=5), limit=6)
    assert len(seen_items) <= 6


def test_users_statistics(client: DatabraryClient):
    _, uid = _resolve_current_user(client)
    if uid is None:
        pytest.skip("Authenticated user id unavailable in search results")

    stats = client.users.statistics(uid)
    assert stats is None or isinstance(stats, UserStatistics)


def test_users_avatar_dest_path(client: DatabraryClient, tmp_path: Path):
    _, uid = _resolve_current_user(client)
    if uid is None:
        pytest.skip("Authenticated user id unavailable in search results")

    dest = tmp_path / "avatar.jpg"
    saved = client.users.avatar(uid, dest_path=str(dest))
    assert Path(saved).exists() or dest.exists() or saved == str(dest)
