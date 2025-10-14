"""Folder models for Databrary API."""

from __future__ import annotations

from pydantic import BaseModel


class Folder(BaseModel):
    """Folder list/detail fields (FolderSerializer)."""

    id: int
    name: str | None = None
    volume: int | None = None
    release_level: str | None = None
    created_at: object | None = None
    updated_at: object | None = None
    source_date: str | None = None

    file_count: int | None = None
    accessible_file_count: int | None = None
    has_full_access: bool | None = None
    contains_different_release_levels: bool | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}
