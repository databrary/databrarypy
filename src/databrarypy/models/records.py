"""Record and measure models for Databrary API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Age(BaseModel):
    """Age structure from AgeSerializer.

    Expect **snake_case** keys, matching JSON after the client's default
    :func:`~databrarypy.utils.case.snake_keys` normalization of API camelCase.
    """

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
    volume_name: str | None = None
    category_id: int
    measures: dict[str, Any] = Field(default_factory=dict)
    birthday: dict[str, Any] | str | None = None
    age: Age | None = None
    default_sessions: list[dict[str, Any]] = Field(default_factory=list)
    record_source_kind: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


# ---------------------------------------------------------------------------
# Write-side models
# ---------------------------------------------------------------------------


class BirthdayInput(BaseModel):
    """Birthday date components for participant record creation/update (snake_case)."""

    year: int
    month: int | None = None
    day: int | None = None
    is_estimated: bool | None = None

    model_config = {"extra": "forbid"}


class AgeInput(BaseModel):
    """Age components for participant record creation/update."""

    years: int = 0
    months: int = 0
    days: int = 0

    model_config = {"extra": "forbid"}


class ParticipantInput(BaseModel):
    """Participant-specific fields (birthday xor age) for create/update.

    Only one of ``birthday`` or ``age`` should be provided.
    """

    birthday: BirthdayInput | None = None
    age: AgeInput | None = None

    model_config = {"extra": "forbid"}


class DateMeasureValue(BaseModel):
    """Structured date value for a metric of type *date* (snake_case)."""

    year: int
    month: int | None = None
    day: int | None = None
    is_estimated: bool | None = None

    model_config = {"extra": "forbid"}
