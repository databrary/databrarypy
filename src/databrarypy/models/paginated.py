"""Generic paginated response model to match DatabraryPagination."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic page wrapper for list endpoints using DatabraryPagination."""

    count: int
    next: str | None
    previous: str | None
    results: list[T]
    total_pages: int | None = None
    current_page: int | None = None
    sort_by: str | None = None
    sort_order: str | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
