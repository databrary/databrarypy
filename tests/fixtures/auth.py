"""Authentication test fixtures."""

import httpx

from .common import build_transport

# Mock authentication response data
MOCK_AUTH_RESPONSES = {
    "token_success": {
        "access_token": "ACCESS_TOKEN",
        "refresh_token": "REFRESH_TOKEN",
        "expires_in": 3600,
    },
    "token_refreshed": {
        "access_token": "REFRESHED_ACCESS_TOKEN",
        "refresh_token": "NEW_REFRESH_TOKEN",
        "expires_in": 3600,
    },
    "token_no_refresh": {
        "access_token": "ACCESS_TOKEN",
        "refresh_token": None,
        "expires_in": 3600,
    },
    "token_error": {
        "error": "invalid_client",
        "error_description": "Client authentication failed",
    },
}


# Handler functions for authentication endpoints
def handle_token_success(request: httpx.Request) -> httpx.Response:
    """Handle successful token requests (password and refresh)."""
    data = request.content.decode()
    if "grant_type=password" in data:
        return httpx.Response(200, json=MOCK_AUTH_RESPONSES["token_success"])
    if "grant_type=refresh_token" in data:
        return httpx.Response(200, json=MOCK_AUTH_RESPONSES["token_refreshed"])
    return httpx.Response(400, json={"error": "unsupported_grant_type"})


def handle_token_error(request: httpx.Request) -> httpx.Response:
    """Handle token request errors."""
    return httpx.Response(401, json=MOCK_AUTH_RESPONSES["token_error"])


# Transport builders for authentication tests
def build_auth_transport(token_handler=handle_token_success, additional_routes=None):
    """Build transport for authentication tests.

    Args:
        token_handler: Handler for /o/token/ endpoint.
        additional_routes: Optional list of (method, path, handler) tuples.
    """
    routes = [("POST", "/o/token/", token_handler)]
    if additional_routes:
        routes.extend(additional_routes)
    return build_transport(*routes)


# Assertion helpers for authentication
def assert_token_headers(request: httpx.Request, user_agent: str = "test"):
    """Assert token request has correct headers."""
    assert request.headers.get("User-Agent") == user_agent
    assert request.headers.get("Accept") == "application/json"
    assert request.headers.get("Content-Type") == "application/x-www-form-urlencoded"


def assert_auth_headers(request: httpx.Request, user_agent: str = "test"):
    """Assert authenticated request has correct headers."""
    assert request.headers.get("User-Agent") == user_agent
    assert request.headers.get("Accept") == "application/json"
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Bearer ")
