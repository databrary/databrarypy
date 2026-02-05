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
    user: UserSlim
    sort_order: int
    volume: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}
