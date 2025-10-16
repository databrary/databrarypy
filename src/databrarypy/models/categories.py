"""Pydantic models for Category and Metric entities."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """Metric model from MetricSerializer fields."""

    id: int
    name: str
    release: str | None = None
    # Data type of the metric's value (e.g., "number", "choice", "string").
    type: str
    # Allowed values for the metric when type is "choice".
    options: list[str] | None = None
    # Default/assumed value when missing.
    assumed: str | int | bool | None = None
    description: str | None = None
    required: bool | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class Category(BaseModel):
    """Category model including nested metrics."""

    id: int
    name: str
    description: str | None = None
    metrics: list[Metric] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "forbid"}
