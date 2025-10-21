"""Tests for DatabraryClient."""

from unittest.mock import Mock

import pytest

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


def test_client_requires_open_state_for_headers():
    """DatabraryClient should raise if used after close."""
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

    client.close()

    with pytest.raises(RuntimeError):
        client._headers()


def test_client_close_is_idempotent():
    """Calling close twice should not re-close underlying clients."""
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

    client.close()
    assert client._closed is True

    client.auth.close = Mock()
    client._http.close = Mock()

    client.close()

    client.auth.close.assert_not_called()
    client._http.close.assert_not_called()


def test_client_context_manager_closes_client():
    """Context manager should return self and close on exit."""
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

    with client as context_client:
        assert context_client is client
        context_client.auth.login()
        who = context_client.whoami()
        assert who.user == MOCK_CLIENT_RESPONSES["whoami"]["user"]

    assert client._closed is True
