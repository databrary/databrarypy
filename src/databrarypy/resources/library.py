"""Library resource for Databrary statistics and metadata."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from ..models import GroupedFormats, LibraryStats


class LibraryResource:
    """Resource for library-wide operations and metadata.

    Provides access to Databrary library statistics and asset format information.
    """

    def __init__(self, http: httpx.Client, headers_fn: Callable[[], dict[str, str]]) -> None:
        """Initialize the library resource.

        Args:
            http: HTTP client for making requests.
            headers_fn: Callable that returns authentication headers.
        """
        self._http = http
        self._headers = headers_fn

    def get_db_stats(self) -> LibraryStats:
        """Get Databrary library statistics.

        Returns:
            LibraryStats containing institution, affiliate, and investigator counts.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        resp = self._http.get("/statistics/summary/", headers=self._headers())
        resp.raise_for_status()
        data: Any = resp.json()
        return LibraryStats.model_validate(data)

    def list_asset_formats(self) -> GroupedFormats:
        """Get available asset formats grouped by category.

        Returns:
            GroupedFormats mapping category names to lists of Format objects.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        resp = self._http.get("/grouped-formats/", headers=self._headers())
        resp.raise_for_status()
        return GroupedFormats.model_validate(resp.json())
