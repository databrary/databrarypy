"""Models for funder entities and volume funding relations."""

from __future__ import annotations

from pydantic import BaseModel


class Funder(BaseModel):
    """Funder entity as exposed by the API."""

    id: int
    name: str
    is_approved: bool

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
