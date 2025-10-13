"""Session models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Session(BaseModel):
    """Session list/detail fields (SessionSerializer)."""

    id: int
    name: str | None = None
    volume: int | None = None
    release_level: str | None = None
    created_at: object | None = None
    updated_at: object | None = None
    source_date: str | None = None
    # Backend may return a structured dict or a blurred string constant
    date: dict[str, Any] | str | None = None

    # Aggregates/flags
    file_count: int | None = None
    accessible_file_count: int | None = None
    has_full_access: bool | None = None
    contains_different_release_levels: bool | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
