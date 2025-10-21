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
    has_avatar: bool | None = None
    has_administrators: bool | None = None
    latitude: float | None = None
    longitude: float | None = None
    manual_coordinates: bool | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class InstitutionRef(BaseModel):
    """Minimal embedded institution fields where nested inside other models."""

    id: int
    name: str
    url: str | None = None
