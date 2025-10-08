"""Generic paginated response model to match DatabraryPagination."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Page(BaseModel):
    """Generic page wrapper for list endpoints using DatabraryPagination."""

    count: int
    next: str | None
    previous: str | None
    results: list[Any]
    total_pages: int
    current_page: int
    sort_by: str | None = None
    sort_order: str | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
