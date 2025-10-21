"""File models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from .formats import Format


class SlimFile(BaseModel):
    """Minimal information about a transcoded asset."""

    id: int
    name: str
    format: dict[str, Any]
    sha1: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class File(BaseModel):
    """File object as returned by FileSerializer (subset)."""

    id: int
    name: str | None = None
    uploader: dict[str, Any] | None = None
    created_at: object | None = None
    updated_at: object | None = None
    upload: dict[str, Any] | None = None
    records: list[dict[str, Any]] | None = None
    release_level: str | None = None
    format: Format | dict[str, Any] | None = None
    source_date: str | None = None
    date: dict[str, Any] | str | None = None
    sha1: str | None = None
    size: int | None = None
    volume: int | None = None
    folder: int | None = None
    session: int | None = None
    mime_type: str | None = None
    transcoded_file: SlimFile | dict[str, Any] | None = None
    has_full_access: bool | None = None
    thumbnail_url: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
