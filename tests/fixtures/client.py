"""Client test fixtures."""

import httpx

from .auth import handle_token_success
from .common import build_transport

# Mock client response data
MOCK_CLIENT_RESPONSES = {
    "whoami": {
        "authMethod": "OAuth2",
        "user": "test@example.org",
    },
}


# Handler functions for client endpoints
def handle_whoami(request: httpx.Request) -> httpx.Response:
    """Handle whoami endpoint."""
    return httpx.Response(200, json=MOCK_CLIENT_RESPONSES["whoami"])


# Transport builder for client tests
def build_client_transport(
    token_handler=handle_token_success,
    whoami_handler=handle_whoami,
):
    """Build transport for client tests.

    Args:
        token_handler: Handler for authentication.
        whoami_handler: Handler for whoami endpoint.
    """
    return build_transport(
        ("POST", "/o/token/", token_handler),
        ("GET", "/oauth2/test/", whoami_handler),
    )
