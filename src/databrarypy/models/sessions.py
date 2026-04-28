"""Session models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .records import Record


class SessionDate(BaseModel):
    """Structured date for a session.

    In staging fixtures this appears as separate year/month/day fields.
    """

    year: int | None = None
    month: int | None = None
    day: int | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class Session(BaseModel):
    """Session list/detail fields (SessionSerializer)."""

    id: int
    name: str
    volume: int
    release_level: str
    created_at: object
    updated_at: object
    source_date: str | None = None
    # The date of the session. Backend may return a structured dict or a blurred string constant.
    date: SessionDate | str | None = None

    file_counts: dict[str, Any]

    # Whether the current user has full access to the session. (some can have blurred names and metadata)

    has_full_access: bool

    # Whether the session contains files with different release levels than the session itself.
    contains_different_release_levels: bool
    # The default records for the session.
    default_records: list[Record] = Field(default_factory=list)
    # The records for the session.
    file_records: list[Record] = Field(default_factory=list)
    source_info: dict[str, Any] | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}
