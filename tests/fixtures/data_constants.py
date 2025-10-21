"""Shared constants and IDs for test fixtures.

This module contains primitive data and IDs used across fixtures
to avoid circular dependencies and magic values.

Note: All data in these fixtures is anonymized and fictional.
No real people, institutions, or identifiers are used.
"""

# ---- Test Entity IDs ----
# User IDs (all anonymized, fictional test data)
USER_ID_1 = 6  # Alex Doe (primary test user)
USER_ID_COAUTHOR = 5  # Jane Smith (coauthor/collaborator)
USER_ID_OWNER = 6  # John Johnson (volume owner) - same ID as USER_ID_1 for compatibility
USER_ID_2 = 7  # Additional test user
USER_ID_NOT_FOUND = 999  # For testing 404 responses

# Convenience aliases
USER_ID_PRIMARY = USER_ID_1

# Institution IDs (all anonymized, fictional institutions)
INSTITUTION_ID_1 = 12  # Example University
INSTITUTION_ID_2 = 23338  # Test Research Institute
INSTITUTION_ID_3 = 23370  # Sample Academic Institution
INSTITUTION_ID_NOT_FOUND = 999  # For testing 404 responses

# Volume IDs
VOLUME_ID_PRIMARY = 1
VOLUME_ID_SECONDARY = 2

# Sponsorship IDs
SPONSORSHIP_ID_1 = 101
INSTITUTION_SPONSORSHIP_ID_1 = 467

# Volume Coauthor IDs
VOLUME_COAUTHOR_ID_1 = 227

# Volume Collaborator IDs
VOLUME_COLLABORATOR_ID_1 = 1

# ---- Common Binary Data ----
MOCK_AVATAR_PNG = b"\x89PNG\r\n\x1a\n"

# ---- Pagination Defaults ----
DEFAULT_PAGE_SIZE = 10
DEFAULT_PAGE_NUMBER = 1

# ---- Processing Task Status ----
TASK_STATUS_PROCESSING = "processing"
