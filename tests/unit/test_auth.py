import time

import pytest

from databrarypy.auth import OAuth2Client

from ..fixtures import (
    MOCK_AUTH_RESPONSES,
    build_auth_transport,
    handle_token_error,
)


def test_oauth2_password_and_refresh_flow():
    """Test successful OAuth2 password grant and token refresh flow."""
    transport = build_auth_transport()

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=transport,
    )

    # Test password grant
    tok1 = oauth.login()
    assert tok1.access_token == MOCK_AUTH_RESPONSES["token_success"]["access_token"]
    assert tok1.refresh_token == MOCK_AUTH_RESPONSES["token_success"]["refresh_token"]
    assert tok1.expires_at > time.time()

    # Test token refresh
    tok2 = oauth.refresh()
    assert tok2.access_token == MOCK_AUTH_RESPONSES["token_refreshed"]["access_token"]
    assert tok2.refresh_token == MOCK_AUTH_RESPONSES["token_refreshed"]["refresh_token"]


def test_token_request_failure():
    """Test that token request failures raise RuntimeError."""
    transport = build_auth_transport(token_handler=handle_token_error)

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="bad_client",
        client_secret="bad_secret",
        username="user@example.org",
        password="password",
        user_agent="test",
        transport=transport,
    )

    with pytest.raises(RuntimeError, match="Token request failed 401"):
        oauth.login()


def test_refresh_without_token():
    """Test that calling refresh without a token raises RuntimeError."""
    transport = build_auth_transport()

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="password",
        user_agent="test",
        transport=transport,
    )

    with pytest.raises(RuntimeError, match="No refresh token available"):
        oauth.refresh()


def test_get_valid_token_without_authentication():
    """Test that getting a token without authentication raises RuntimeError."""
    transport = build_auth_transport()

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="password",
        user_agent="test",
        transport=transport,
    )

    with pytest.raises(RuntimeError, match="Not authenticated"):
        oauth.get_valid_access_token()


def test_expired_token_without_refresh_token():
    """Test that expired token without refresh token raises RuntimeError."""
    import httpx

    def handle_token_no_refresh(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=MOCK_AUTH_RESPONSES["token_no_refresh"])

    transport = build_auth_transport(token_handler=handle_token_no_refresh)

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="password",
        user_agent="test",
        transport=transport,
    )

    # Login with a token that has no refresh token
    oauth.login()

    # Force the token to be expired
    oauth._token.expires_at = time.time() - 100

    with pytest.raises(RuntimeError, match="Access token expired and no refresh token"):
        oauth.get_valid_access_token()


def test_automatic_token_refresh():
    """Test that get_valid_access_token automatically refreshes expired tokens."""
    transport = build_auth_transport()

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="password",
        user_agent="test",
        transport=transport,
    )

    # Login
    oauth.login()
    initial_token = MOCK_AUTH_RESPONSES["token_success"]["access_token"]
    assert oauth._token.access_token == initial_token

    # Force token to be expired
    oauth._token.expires_at = time.time() - 100

    # get_valid_access_token should automatically refresh
    token = oauth.get_valid_access_token()
    refreshed_token = MOCK_AUTH_RESPONSES["token_refreshed"]["access_token"]
    assert token == refreshed_token
    assert oauth._token.access_token == refreshed_token
    assert oauth._token.refresh_token == MOCK_AUTH_RESPONSES["token_refreshed"]["refresh_token"]


def test_oauth2_client_context_manager() -> None:
    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=build_auth_transport(),
    )
    with oauth:
        oauth.login()
    assert oauth._closed is True


def test_oauth2_client_close_idempotent() -> None:
    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=build_auth_transport(),
    )
    oauth.close()
    assert oauth._closed is True
    oauth.close()  # no error should be raised
    assert oauth._closed is True


def test_oauth2_client_rejects_usage_after_close() -> None:
    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        username="user@example.org",
        password="pw",
        user_agent="test",
        transport=build_auth_transport(),
    )
    oauth.close()
    with pytest.raises(RuntimeError, match="OAuth2Client is closed"):
        oauth.login()
