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
from .constants import (
    TEST_BAD_CLIENT_ID,
    TEST_BAD_CLIENT_SECRET,
    TEST_BASE_URL,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)
from .data_constants import (
    INSTITUTION_ID_1,
    INSTITUTION_ID_2,
    INSTITUTION_ID_3,
    INSTITUTION_ID_NOT_FOUND,
    INSTITUTION_SPONSORSHIP_ID_1,
    MOCK_AVATAR_PNG,
    SPONSORSHIP_ID_1,
    USER_ID_1,
    USER_ID_2,
    USER_ID_COAUTHOR,
    USER_ID_NOT_FOUND,
    USER_ID_OWNER,
    USER_ID_PRIMARY,
    VOLUME_COAUTHOR_ID_1,
    VOLUME_COLLABORATOR_ID_1,
    VOLUME_ID_PRIMARY,
    VOLUME_ID_SECONDARY,
)
from .system import (
    MOCK_SYSTEM_RESPONSES,
    build_system_transport,
    handle_formats,
    handle_stats,
)

__all__ = [
    # Credential constants
    "TEST_BASE_URL",
    "TEST_CLIENT_ID",
    "TEST_CLIENT_SECRET",
    "TEST_USERNAME",
    "TEST_PASSWORD",
    "TEST_BAD_CLIENT_ID",
    "TEST_BAD_CLIENT_SECRET",
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
    # Data constants
    "MOCK_AVATAR_PNG",
    "USER_ID_1",
    "USER_ID_PRIMARY",
    "USER_ID_COAUTHOR",
    "USER_ID_OWNER",
    "USER_ID_2",
    "USER_ID_NOT_FOUND",
    "INSTITUTION_ID_1",
    "INSTITUTION_ID_2",
    "INSTITUTION_ID_3",
    "INSTITUTION_ID_NOT_FOUND",
    "VOLUME_ID_PRIMARY",
    "VOLUME_ID_SECONDARY",
    "SPONSORSHIP_ID_1",
    "INSTITUTION_SPONSORSHIP_ID_1",
    "VOLUME_COAUTHOR_ID_1",
    "VOLUME_COLLABORATOR_ID_1",
]
