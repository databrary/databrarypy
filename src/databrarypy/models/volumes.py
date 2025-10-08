"""Models for volume data used in user-related endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class VolumeCoauthor(BaseModel):
    """Coauthor entry for a volume preview."""

    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class VolumePreview(BaseModel):
    """PreviewVolumeSerializer fields."""

    id: int
    updated_at: datetime | None = None
    created_at: datetime | None = None
    title: str
    description: str | None = None
    short_name: str | None = None
    sharing_level: str
    coauthors: list[VolumeCoauthor] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
