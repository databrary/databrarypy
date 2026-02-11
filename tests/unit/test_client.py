"""Tests for DatabraryClient."""

from unittest.mock import Mock, patch

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
        transport=transport,
    )

    with client as context_client:
        assert context_client is client
        context_client.auth.login()
        who = context_client.whoami()
        assert who.user == MOCK_CLIENT_RESPONSES["whoami"]["user"]

    assert client._closed is True


def test_client_default_user_agent():
    """Client uses databrarypy/<version> as User-Agent."""
    transport = build_client_transport()
    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        transport=transport,
    )
    assert client.user_agent.startswith("databrarypy/")
    assert "/" in client.user_agent


def test_client_from_env_success():
    """Test successful client creation from environment variables with explicit BASE_URL."""
    env_vars = {
        "BASE_URL": "https://api.example.org",
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USERNAME": "test@example.org",
        "PASSWORD": "test_password",
    }

    with patch("databrarypy.client.dotenv_values", return_value=env_vars):
        client = DatabraryClient.from_env()

        # Test that the client is created with the correct attributes
        assert client.base_url == "https://api.example.org"
        assert client.user_agent.startswith("databrarypy/")
        assert client.auth.client_id == "test_client_id"
        assert client.auth.client_secret == "test_client_secret"
        assert client.auth.username == "test@example.org"
        assert client.auth.password == "test_password"


def test_client_from_env_with_custom_params():
    """Test client creation from environment with custom parameters."""
    env_vars = {
        "BASE_URL": "https://api.example.org",
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USERNAME": "test@example.org",
        "PASSWORD": "test_password",
    }

    transport = build_client_transport()

    with patch("databrarypy.client.dotenv_values", return_value=env_vars):
        client = DatabraryClient.from_env(
            login=False,
            timeout=60.0,
            transport=transport,
            snake_case=False,
            max_retries=5,
            respect_retry_after=False,
            backoff_base=2.0,
            backoff_jitter=False,
        )

        # Test that the client is created with the correct attributes
        assert client.base_url == "https://api.example.org"
        assert client.user_agent.startswith("databrarypy/")
        assert client.auth.client_id == "test_client_id"
        assert client.auth.client_secret == "test_client_secret"
        assert client.auth.username == "test@example.org"
        assert client.auth.password == "test_password"

        # Test that retry settings are applied to resources
        assert client.system._max_retries == 5
        assert client.system._respect_retry_after is False
        assert client.system._backoff_base == 2.0
        assert client.system._backoff_jitter == 0.0  # False gets converted to 0.0


def test_client_from_env_with_login():
    """Test client creation from environment with login enabled."""
    env_vars = {
        "BASE_URL": "https://api.example.org",
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USERNAME": "test@example.org",
        "PASSWORD": "test_password",
    }

    with (
        patch("databrarypy.client.dotenv_values", return_value=env_vars),
        patch("databrarypy.client.OAuth2Client") as mock_oauth2,
    ):
        mock_auth = Mock()
        mock_oauth2.return_value = mock_auth

        DatabraryClient.from_env(login=True)
        mock_auth.login.assert_called_once()


def test_client_from_env_missing_required_vars():
    """Test client creation fails with missing required environment variables (BASE_URL optional)."""
    # Missing some required variables (BASE_URL is optional)
    env_vars = {
        # No BASE_URL
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        # Missing USERNAME, PASSWORD
    }

    with (
        patch("databrarypy.client.dotenv_values", return_value=env_vars),
        pytest.raises(RuntimeError, match="Missing required configuration values"),
    ):
        DatabraryClient.from_env()


def test_client_from_env_empty_env_file():
    """Test client creation fails with no environment variables."""
    with (
        patch("databrarypy.client.dotenv_values", return_value={}),
        pytest.raises(RuntimeError, match="Missing required configuration values"),
    ):
        DatabraryClient.from_env()


def test_client_from_env_with_none_values():
    """Test client creation fails with None values in environment (BASE_URL may be None)."""
    env_vars = {
        "BASE_URL": None,  # should fall back to default
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USERNAME": "test@example.org",
        "PASSWORD": "test_password",
    }

    with patch("databrarypy.client.dotenv_values", return_value=env_vars):
        client = DatabraryClient.from_env()
        assert client.base_url == "https://api.databrary.org"


def test_client_from_env_uses_default_user_agent():
    """from_env uses databrarypy/<version> as User-Agent."""
    env_vars = {
        "BASE_URL": "https://api.example.org",
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USERNAME": "test@example.org",
        "PASSWORD": "test_password",
    }
    with patch("databrarypy.client.dotenv_values", return_value=env_vars):
        client = DatabraryClient.from_env()
        assert client.user_agent.startswith("databrarypy/")


def test_client_from_env_with_env_file_path():
    """Test client creation with custom env file path."""
    env_vars = {
        "BASE_URL": "https://api.example.org",
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USERNAME": "test@example.org",
        "PASSWORD": "test_password",
    }

    with patch("databrarypy.client.dotenv_values") as mock_dotenv:
        mock_dotenv.return_value = env_vars
        client = DatabraryClient.from_env(env_file="/path/to/.env")

        mock_dotenv.assert_called_once_with("/path/to/.env")
        assert client.base_url == "https://api.example.org"
        assert client.auth.client_id == "test_client_id"
