"""Factories for common test payloads."""

from __future__ import annotations

from typing import Any


def make_page(results: list[Any], **overrides: Any) -> dict[str, Any]:
    """Create a paginated payload dict with sensible defaults."""
    count = overrides.pop("count", len(results))
    page: dict[str, Any] = {
        "count": count,
        "next": None,
        "previous": None,
        "results": results,
    }
    page.update(overrides)
    return page
