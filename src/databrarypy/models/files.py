"""File models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .formats import Format
from .records import Record
from .users import UserSlim


class UploaderRef(BaseModel):
    """Minimal uploader representation embedded on file rows."""

    id: int
    first_name: str | None = None
    last_name: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class SlimFile(BaseModel):
    """Minimal information about a transcoded asset."""

    id: int
    name: str
    format: dict[str, Any]
    sha1: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class FileWrite(BaseModel):
    """Writable fields for file PUT/PATCH (mirrors FileWriteSerializer).

    Sessions honor the full set; folders (which use FileSerializer for writes)
    effectively only honor ``name`` and ``release_level``.
    """

    name: str | None = None
    release_level: str | None = None
    source_date: str | None = None
    date: dict[str, Any] | None = None
    date_precision: str | None = None
    is_estimated: bool | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}

    def to_patch_payload(self) -> dict[str, Any]:
        """Serialize for PATCH: only keys with non-None values.

        Session file PUT builds its body explicitly (omit unset fields); do not
        use ``model_dump(exclude_none=False)`` for PUT or the API may interpret
        JSON ``null`` as clearing nullable metadata.
        """
        return self.model_dump(exclude_none=True)


class File(BaseModel):
    """File object as returned by FileSerializer (subset)."""

    id: int
    name: str
    uploader: UploaderRef | UserSlim | None = None
    created_at: object | None = None
    updated_at: object | None = None
    upload: dict[str, Any] | None = None
    records: list[Record] | None = None
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
    source_info: dict[str, Any] | None = None
    linked_destinations: list[dict[str, Any]] = Field(default_factory=list)
    is_added_file: bool | None = None
    link_kind: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}
