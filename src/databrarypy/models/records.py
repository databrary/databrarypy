"""Record and measure models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Age(BaseModel):
    """Age structure from AgeSerializer."""

    # The age in years, months, and days. Example: 1 year, 2 months, 3 days.
    years: int | None = None
    months: int | None = None
    days: int | None = None

    # The age in days. Example: 365 days.
    total_days: int | None = None
    formatted_value: str | None = None
    is_estimated: bool | None = None
    is_blurred: bool | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class Record(BaseModel):
    """Record fields (RecordSerializer read representation)."""

    id: int
    volume: int
    category_id: int
    measures: dict[str, Any] = Field(default_factory=dict)
    birthday: dict[str, Any] | str | None = None
    age: Age | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}
