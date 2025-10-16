"""Volume coauthor models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from .users import UserSlim


class VolumeCoauthor(BaseModel):
    """Coauthor entry; accepts nested user or user_id.

    Used in `VolumePreview` and `VolumeDetail` responses.
    """

    id: int
    user: UserSlim | None = None
    user_id: int | None = None
    sort_order: int | None = None
    volume: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
