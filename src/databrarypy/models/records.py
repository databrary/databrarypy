"""Record and measure models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Age(BaseModel):
    """Age structure from AgeSerializer."""

    years: int | None = None
    months: int | None = None
    days: int | None = None
    total_days: int | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Record(BaseModel):
    """Record fields (RecordSerializer read representation)."""

    id: int
    volume: int
    category_id: int
    measures: dict[str, Any] = Field(default_factory=dict)
    birthday: dict[str, Any] | str | None = None
    age: Age | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
