"""Shared credential constants used across all unit tests.

All values are intentionally fake and are only used with mock httpx transports.
"""

TEST_BASE_URL = "https://api.example.org"
TEST_CLIENT_ID = "test-client-id"
TEST_CLIENT_SECRET = "test-client-secret"
TEST_USERNAME = "test@example.org"
TEST_PASSWORD = "test-password"

# Used by auth failure-path tests
TEST_BAD_CLIENT_ID = "bad-test-client-id"
TEST_BAD_CLIENT_SECRET = "bad-test-client-secret"
