"""Models for institution-related data."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class Institution(BaseModel):
    """Institution as returned by InstitutionSerializer."""

    id: int
    name: str
    url: str | None = None
    date_signed: date | None = None
    source: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    has_avatar: bool
    has_administrators: bool
    latitude: float | None = None
    longitude: float | None = None
    manual_coordinates: bool

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
