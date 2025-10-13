"""Activity/history models for volume and user history endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class HistoryUser(BaseModel):
    """Slim user info embedded in history records."""

    id: int | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class VolumeActivityItem(BaseModel):
    """Structured volume history item with common historical fields.

    Covers types emitted by CombinedVolumeHistorySerializer, such as:
    'volume_change', 'session_change', 'folder_change', 'coauthor_change',
    'collaborator_change', 'funding_change', 'link_change',
    'ownership_transfer_change', 'volume_metric_change', 'tag_change'.
    """

    type: str
    timestamp: str

    # Common historical fields
    history_id: int | None = None
    history_user: HistoryUser | None = None
    ip_address: str | None = None

    # Common change payload
    changed_fields: list[str] | None = None
    changed_data: dict[str, Any] | None = None

    # Frequently present fields per model
    volume_id: int | None = None
    name: str | None = None
    deleted_at: str | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class UserActivityItem(BaseModel):
    """Structured user history item.

    Combined user activity includes login attempts and historical user/sponsorship
    changes. This model captures common fields and allows extras.
    """

    type: str
    timestamp: str | None = None

    # Login attempt fields
    id: int | None = None
    email: str | None = None
    ip_address: str | None = None
    successful: bool | None = None

    # Historical user change fields
    history_id: int | None = None
    history_user: HistoryUser | None = None
    changed_fields: list[str] | None = None
    changed_data: dict[str, Any] | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}
