"""Pydantic models for Tag entities."""

from __future__ import annotations

from pydantic import BaseModel


class Tag(BaseModel):
    """Simple tag model matching TagSerializer."""

    id: int
    name: str

    model_config = {"populate_by_name": True, "extra": "forbid"}
