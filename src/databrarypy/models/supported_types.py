"""Pydantic models for supported file types, derived from grouped formats."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SupportedFileType(BaseModel):
    """Flattened supported file type row.

    Matches the R get_supported_file_types() output conceptually
    (asset_type, asset_type_id, mimetype, extensions).
    """

    asset_type_id: int
    asset_type: str
    mimetype: str
    extensions: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "forbid"}


class SupportedFileTypes(BaseModel):
    """A collection of supported file type entries."""

    items: list[SupportedFileType] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "forbid"}
