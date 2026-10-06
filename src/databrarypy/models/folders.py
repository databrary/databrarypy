"""Folder models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FolderDuplicateFileCheckItem(BaseModel):
    """One entry from the folder check-duplicate-files endpoint."""

    filename: str
    exists: bool

    model_config = {"extra": "forbid"}


class Folder(BaseModel):
    """Folder list/detail fields (FolderSerializer)."""

    id: int
    name: str | None = None
    volume: int
    release_level: str
    created_at: object
    updated_at: object
    source_date: str | None = None

    file_counts: dict[str, Any]
    has_full_access: bool
    contains_different_release_levels: bool
    source_info: dict[str, Any] | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class FolderMutation(BaseModel):
    """Fields returned when creating or updating a folder (``FolderWriteSerializer``).

    Narrower than :class:`Folder`, which list/detail GET responses populate with
    ``volume``, ``file_counts``, ``has_full_access``, etc.
    """

    id: int | None = None
    name: str | None = None
    release_level: str | None = None
    source_date: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
