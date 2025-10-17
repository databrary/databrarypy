"""Test fixtures for databrarypy tests."""

from .auth import (
    MOCK_AUTH_RESPONSES,
    build_auth_transport,
    handle_token_error,
    handle_token_success,
)
from .client import (
    MOCK_CLIENT_RESPONSES,
    build_client_transport,
    handle_whoami,
)
from .common import build_transport, handle_not_found
from .system import (
    MOCK_SYSTEM_RESPONSES,
    build_system_transport,
    handle_formats,
    handle_stats,
)

__all__ = [
    # Common fixtures
    "build_transport",
    "handle_not_found",
    # Auth fixtures
    "MOCK_AUTH_RESPONSES",
    "build_auth_transport",
    "handle_token_error",
    "handle_token_success",
    # Client fixtures
    "MOCK_CLIENT_RESPONSES",
    "build_client_transport",
    "handle_whoami",
    # System fixtures
    "MOCK_SYSTEM_RESPONSES",
    "build_system_transport",
    "handle_formats",
    "handle_stats",
]
