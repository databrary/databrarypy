"""Pydantic models for Category and Metric entities."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """Metric model from MetricSerializer fields."""

    id: int
    name: str
    release: str | None = None
    type: str | None = None
    options: Any | None = None
    assumed: Any | None = None
    description: str | None = None
    required: bool | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Category(BaseModel):
    """Category model including nested metrics."""

    id: int
    name: str
    description: str | None = None
    metrics: list[Metric] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "ignore"}
