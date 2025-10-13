"""Tests for SystemResource."""

from databrarypy.client import DatabraryClient

from .fixtures import MOCK_SYSTEM_RESPONSES, build_system_transport


def test_get_db_stats():
    """Test system statistics retrieval."""
    transport = build_system_transport()

    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=transport,
    )

    client.auth.login()

    # Test stats
    stats = client.system.get_db_stats()
    expected_stats = MOCK_SYSTEM_RESPONSES["stats"]
    assert stats.institutions == expected_stats["institutions"]
    assert stats.affiliates == expected_stats["affiliates"]
    assert stats.investigators == expected_stats["investigators"]
    assert stats.hours_of_recordings == expected_stats["hours_of_recordings"]


def test_list_asset_formats():
    """Test listing asset formats grouped by category."""
    transport = build_system_transport()

    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=transport,
    )

    client.auth.login()

    # Get grouped formats
    grouped = client.system.list_asset_formats()
    data = grouped.root

    # Verify structure
    expected_formats = MOCK_SYSTEM_RESPONSES["formats"]
    assert "Video" in data
    assert "Audio" in data
    assert "Image" in data

    # Verify Video formats
    assert len(data["Video"]) == len(expected_formats["Video"])
    assert data["Video"][0].mimetype == expected_formats["Video"][0]["mimetype"]
    assert data["Video"][0].name == expected_formats["Video"][0]["name"]
    assert data["Video"][0].extensions == expected_formats["Video"][0]["extensions"]
    assert data["Video"][1].mimetype == expected_formats["Video"][1]["mimetype"]

    # Verify Audio formats
    assert len(data["Audio"]) == len(expected_formats["Audio"])
    assert data["Audio"][0].mimetype == expected_formats["Audio"][0]["mimetype"]
    assert data["Audio"][0].name == expected_formats["Audio"][0]["name"]
    assert data["Audio"][1].mimetype == expected_formats["Audio"][1]["mimetype"]

    # Verify Image formats
    assert len(data["Image"]) == len(expected_formats["Image"])
    assert data["Image"][0].mimetype == expected_formats["Image"][0]["mimetype"]
    assert data["Image"][0].extensions == expected_formats["Image"][0]["extensions"]


def test_get_supported_file_types():
    """Test flattening of supported file types from grouped formats."""
    transport = build_system_transport()

    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=transport,
    )

    client.auth.login()

    supported = client.system.get_supported_file_types()
    items = supported.items

    # Verify count equals sum of all grouped entries
    total = sum(len(v) for v in MOCK_SYSTEM_RESPONSES["formats"].values())
    assert len(items) == total

    # Verify first few items map correctly
    first = items[0]
    expected_first = MOCK_SYSTEM_RESPONSES["formats"]["Video"][0]
    assert first.asset_type_id == expected_first["id"]
    assert first.asset_type == expected_first["name"]
    assert first.mimetype == expected_first["mimetype"]
    assert first.extensions == expected_first["extensions"]


def test_get_permission_and_release_levels():
    """Test client-side constants for permission and release levels."""
    transport = build_system_transport()

    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=transport,
    )

    client.auth.login()

    perms = client.system.get_permission_levels()
    assert "owner" in perms.volume_access_levels
    assert "read write" in perms.volume_collaborator_access_levels

    releases = client.system.get_release_levels()
    codes = [lvl.code for lvl in releases.levels]
    assert codes == ["private", "authorized_users", "learning_audiences", "public"]


def test_is_healthy_true_and_false():
    transport = build_system_transport()

    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        user_agent="test",
        transport=transport,
    )

    client.auth.login_with_password("user@example.org", "pw")

    # True case is covered separately; here simulate non-200 using explicit handler to cover branch
    from .fixtures.auth import handle_token_success
    from .fixtures.common import build_transport, handle_not_found

    def handle_health(_request):
        return handle_not_found(_request)

    failing_transport = build_transport(
        ("POST", "/o/token/", handle_token_success), ("GET", "/health/", handle_health)
    )

    client_fail = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        user_agent="test",
        transport=failing_transport,
    )
    client_fail.auth.login_with_password("user@example.org", "pw")
    assert client_fail.system.is_healthy() is False

    # Now simulate an exception during the request to cover except path
    def raise_exc(_request):
        raise RuntimeError("network failure")

    exc_transport = build_transport(
        ("POST", "/o/token/", handle_token_success), ("GET", "/health/", raise_exc)
    )
    client_exc = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        user_agent="test",
        transport=exc_transport,
    )
    client_exc.auth.login_with_password("user@example.org", "pw")
    assert client_exc.system.is_healthy() is False
