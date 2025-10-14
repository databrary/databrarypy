"""Session models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .records import Record


class Session(BaseModel):
    """Session list/detail fields (SessionSerializer)."""

    id: int
    name: str | None = None
    volume: int | None = None
    release_level: str | None = None
    created_at: object | None = None
    updated_at: object | None = None
    source_date: str | None = None

    # The date of the session. Backend may return a structured dict or a blurred string constant.
    date: dict[str, Any] | str | None = None

    # The total number of files directly in this session.
    file_count: int | None = None

    # The number of files the current user can access.
    accessible_file_count: int | None = None

    # Whether the current user has full access to the session. (some can have blurred names and metadata)
    has_full_access: bool | None = None

    # Whether the session contains files with different release levels than the session itself.
    contains_different_release_levels: bool | None = None
    # Additional aggregates
    default_records: list[Record] = Field(default_factory=list)
    file_records: list[Record] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "forbid"}
