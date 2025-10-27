"""Folder models for Databrary API."""

from __future__ import annotations

from pydantic import BaseModel


class Folder(BaseModel):
    """Folder list/detail fields (FolderSerializer)."""

    id: int
    name: str
    volume: int
    release_level: str
    created_at: object
    updated_at: object
    source_date: str | None = None

    file_count: int
    accessible_file_count: int
    has_full_access: bool
    contains_different_release_levels: bool

    model_config = {"populate_by_name": True, "extra": "forbid"}
