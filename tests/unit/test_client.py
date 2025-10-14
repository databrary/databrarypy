"""Tests for DatabraryClient."""

from databrarypy.client import DatabraryClient

from ..fixtures import MOCK_CLIENT_RESPONSES, build_client_transport


def test_client_initialization_and_whoami():
    """Test client initialization and whoami endpoint."""
    transport = build_client_transport()

    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=transport,
    )

    # Login
    client.auth.login()

    # Test whoami
    who = client.whoami()
    assert who.auth_method == MOCK_CLIENT_RESPONSES["whoami"]["authMethod"]
    assert who.user == MOCK_CLIENT_RESPONSES["whoami"]["user"]
