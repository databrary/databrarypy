"""Shared pytest fixtures/helpers for tests."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from databrarypy.models.paginated import Page


def first_page_item(page: Page[Any]) -> Any | None:
    """Return the first item from an object exposing ``results``."""

    return next(iter(page.results), None)


def first_list_item(iterable: Iterable[Any]) -> Any | None:
    """Return the first item from an iterable."""

    return next(iter(iterable), None)


def collect_items(iterable: Iterable[Any], limit: int) -> list[Any]:
    """Collect items from the iterable up to ``limit`` elements."""

    collected: list[Any] = []
    for idx, item in enumerate(iterable):
        collected.append(item)
        if idx + 1 >= limit:
            break
    return collected
