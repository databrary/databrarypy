"""Volume collaborators fixtures and handlers."""

from __future__ import annotations

import httpx

from .data_constants import (
    VOLUME_COLLABORATOR_ID_1,
    VOLUME_ID_PRIMARY,
)
from .users import MOCK_USER_COAUTHOR, MOCK_USER_OWNER

MOCK_COLLABORATORS_1 = [
    {
        "id": VOLUME_COLLABORATOR_ID_1,
        "volume": VOLUME_ID_PRIMARY,
        "user": MOCK_USER_COAUTHOR,
        "sponsor": MOCK_USER_OWNER,
        "sponsorship": None,
        "is_publicly_visible": True,
        "access_level": "investigator",
        "expiration_date": "2026-03-05",
    }
]


def handle_volume_collaborators_1(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_COLLABORATORS_1)


def handle_volume_collaborator_1(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_COLLABORATORS_1[0])
