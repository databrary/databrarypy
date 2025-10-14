"""Shared volume-related models (links, funding, categories, counts, citation)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .funders import Funder


class VolumeLink(BaseModel):
    """External link attached to a volume."""

    id: int | None = None
    title: str
    url: str

    model_config = {"populate_by_name": True, "extra": "forbid"}


class VolumeFundingRead(BaseModel):
    """Read-only representation of a volume funding record with nested funder."""

    funder: Funder
    awards: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class Metric(BaseModel):
    """Metric serializer fields (subset)."""

    id: int
    name: str
    release: str
    type: str
    options: list[str] | None = None
    assumed: str | None = None
    description: str | None = None
    required: bool | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class Category(BaseModel):
    """Category with nested metrics enabled for a volume."""

    id: int
    name: str
    description: str | None = None
    metrics: list[Metric] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "forbid"}


class FileCountsBreakdown(BaseModel):
    """Breakdown of file counts by release level for a type (session/folder)."""

    private: int
    authorized_users: int
    learning_audiences: int
    public: int


class FileCounts(BaseModel):
    """Aggregated file counts for a volume by entity type."""

    session: FileCountsBreakdown
    folder: FileCountsBreakdown


class Citation(BaseModel):
    """Structured citation object returned by the backend."""

    authors: str
    year: int
    title: str
    institution: str | None = None
    retrieval_date: str | None = None
    volume_id: int | None = None
