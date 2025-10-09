"""System resource for Databrary statistics and metadata."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from ..models import (
    GroupedFormats,
    PermissionLevels,
    ReleaseLevels,
    Stats,
    SupportedFileType,
    SupportedFileTypes,
)
from ._base import BaseResource


class SystemResource(BaseResource):
    """Resource for system-wide operations and metadata.

    Provides access to Databrary system statistics and asset format information.
    """

    def __init__(
        self,
        http: httpx.Client,
        headers_fn: Callable[[], dict[str, str]],
        normalize_json: Callable[[Any], Any],
    ) -> None:
        """Initialize the system resource.

        Args:
            http: HTTP client for making requests.
            headers_fn: Callable that returns authentication headers.
            normalize_json: Callable to normalize JSON keys (e.g., camelCase->snake_case).
        """
        super().__init__(http, headers_fn, normalize_json)

    def get_db_stats(self) -> Stats:
        """Get Databrary system statistics.

        Returns:
            Stats containing institution, affiliate, and investigator counts.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        data: Any = self._get_json("/statistics/summary/")
        return Stats.model_validate(data)

    def list_asset_formats(self) -> GroupedFormats:
        """Get available asset formats grouped by category.

        Returns:
            GroupedFormats mapping category names to lists of Format objects.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        # Keep category keys as-is (e.g., 'Video', 'Audio'), so bypass normalization.
        data = self._raw_get_json("/grouped-formats/")
        return GroupedFormats.model_validate(data)

    def get_supported_file_types(self) -> SupportedFileTypes:
        """Return supported file types flattened from grouped formats.

        Derives from the grouped formats endpoint on the server.
        """
        grouped = self.list_asset_formats().root
        items: list[SupportedFileType] = []
        # Flatten grouped formats into SupportedFileType rows
        for _category, formats in grouped.items():
            for fmt in formats:
                items.append(
                    SupportedFileType(
                        asset_type_id=fmt.id,
                        asset_type=fmt.name,
                        mimetype=fmt.mimetype,
                        extensions=fmt.extensions,
                    )
                )
        return SupportedFileTypes(items=items)

    def get_permission_levels(self) -> PermissionLevels:
        """Return client-side permission level constants.

        Mirrors backend VolumeAccessLevel and VolumeCollaboratorAccessLevel enums.
        """
        return PermissionLevels()

    def get_release_levels(self) -> ReleaseLevels:
        """Return client-side release level constants.

        Mirrors backend FileSharingLevel enum.
        """
        return ReleaseLevels()
