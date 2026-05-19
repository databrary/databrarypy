"""Models for per-entity statistics data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class _StatisticsBase(BaseModel):
    """Shared fields for entity statistics (institution / user)."""

    volumes_number: int
    files_number: int
    uploaded_data_footprint: int
    transcoded_data_footprint: int
    soft_deleted_uploaded_data_footprint: int
    soft_deleted_transcoded_data_footprint: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class InstitutionStatistics(_StatisticsBase):
    """Statistics for a single institution as returned by the backend."""

    institution_id: int


class UserStatistics(_StatisticsBase):
    """Statistics for a single user as returned by the backend."""

    user_id: int
