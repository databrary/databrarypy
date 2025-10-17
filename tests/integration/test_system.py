from __future__ import annotations

from databrarypy.client import DatabraryClient


def test_system_stats_and_formats(client: DatabraryClient):
    stats = client.system.get_db_stats()
    assert stats.institutions >= 0

    grouped = client.system.list_asset_formats()
    assert isinstance(grouped.root, dict)

    supported = client.system.get_supported_file_types()
    assert len(supported.items) >= 0


def test_system_health(client: DatabraryClient):
    assert client.system.is_healthy() in (True, False)


def test_system_permission_and_release_levels(client: DatabraryClient):
    perms = client.system.get_permission_levels()
    assert isinstance(perms.volume_access_levels, list)
    assert "read only" in perms.volume_access_levels

    rel = client.system.get_release_levels()
    assert any(level.code == "public" for level in rel.levels)
