"""Volumes resource for Databrary API."""

from __future__ import annotations

import builtins
from typing import Iterator

from ..models import (
    Category,
    Page,
    VolumeActivityItem,
    VolumeCollaborator,
    VolumeDetail,
    VolumeFundingRead,
    VolumeLink,
    VolumeListItem,
)
from ..models.downloads import ProcessingTask
from ._base import BaseResource


class VolumesResource(BaseResource):
    """Resource for volume operations and relations (excluding sessions/downloads)."""

    def page(
        self,
        *,
        search: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[VolumeListItem]:
        """List related volumes for the authenticated user (paginated)."""
        params = self.build_params(search=search, ordering=ordering, page=page, page_size=page_size)
        return self._get_page("/volumes/", params=params, parser=VolumeListItem.model_validate)

    def list(
        self,
        *,
        search: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Iterator[VolumeListItem]:
        """Iterate all volumes across pages yielding `VolumeListItem` objects."""
        params = self.build_params(search=search, ordering=ordering, page=page, page_size=page_size)
        return self.paginate_items("/volumes/", params=params, parser=VolumeListItem.model_validate)

    def retrieve(self, volume_id: int) -> VolumeDetail:
        """Retrieve full volume details by id."""
        data = self._get_json(f"/volumes/{volume_id}/")
        return VolumeDetail.model_validate(data)

    def tags(self, volume_id: int) -> builtins.list[str]:
        """Get tag names assigned to the volume."""
        data = self._get_json(f"/volumes/{volume_id}/tags/")
        return list(data)

    def links(self, volume_id: int) -> builtins.list[VolumeLink]:
        """List links for the volume."""
        data = self._get_json(f"/volumes/{volume_id}/links/")
        return [VolumeLink.model_validate(item) for item in data]

    # Fundings
    def fundings(self, volume_id: int) -> builtins.list[VolumeFundingRead]:
        """List volume fundings (typed objects)."""
        data = self._get_json(f"/volumes/{volume_id}/fundings/")
        return [VolumeFundingRead.model_validate(item) for item in data]

    def collaborators(self, volume_id: int) -> builtins.list[VolumeCollaborator]:
        """List collaborators visible to the current user for the volume."""
        data = self._get_json(f"/volumes/{volume_id}/collaborators/")
        return [VolumeCollaborator.model_validate(item) for item in data]

    def collaborator(self, volume_id: int, collaborator_id: int) -> VolumeCollaborator:
        """Retrieve a specific collaborator by id."""
        data = self._get_json(f"/volumes/{volume_id}/collaborators/{collaborator_id}/")
        return VolumeCollaborator.model_validate(data)

    # Activity/history
    def activity_page(
        self,
        volume_id: int,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[VolumeActivityItem]:
        """List combined activity for a volume (sessions, folders, links, etc.)."""
        params = self.build_params(page=page, page_size=page_size)
        return self._get_page(
            f"/volumes/{volume_id}/history/",
            params=params,
            parser=VolumeActivityItem.model_validate,
        )

    def activity_list(
        self,
        volume_id: int,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Iterator[VolumeActivityItem]:
        """Iterate combined activity for a volume across pages yielding `VolumeActivityItem`."""
        params = self.build_params(page=page, page_size=page_size)
        return self.paginate_items(
            f"/volumes/{volume_id}/history/",
            params=params,
            parser=VolumeActivityItem.model_validate,
        )

    # ---------------------------
    # Volume categories
    # ---------------------------

    def get_enabled_categories(self, volume_id: int) -> builtins.list[Category]:
        """List categories currently enabled for a volume."""
        data = self._get_json(f"/volumes/{volume_id}/")
        items = data.get("enabled_categories") or [] if isinstance(data, dict) else []
        return [Category.model_validate(c) for c in items]

    def set_enabled_categories(
        self,
        volume_id: int,
        category_ids: builtins.list[int],
    ) -> None:
        """Replace the volume's enabled categories with the given list.

        This is a full replacement -- categories not in *category_ids* will be
        disabled.  Pass an empty list to disable all categories.
        """
        self._post_json(f"/volumes/{volume_id}/categories/", json=category_ids)

    def enable_category(self, volume_id: int, category_id: int) -> None:
        """Add a single category to the volume's enabled set (additive).

        No-op if the category is already enabled.
        """
        current = self.get_enabled_categories(volume_id)
        current_ids = [c.id for c in current]
        if category_id not in current_ids:
            current_ids.append(category_id)
            self.set_enabled_categories(volume_id, current_ids)

    def disable_category(self, volume_id: int, category_id: int) -> None:
        """Remove a single category from the volume's enabled set.

        No-op if the category is not currently enabled.
        """
        current = self.get_enabled_categories(volume_id)
        updated_ids = [c.id for c in current if c.id != category_id]
        if len(updated_ids) != len(current):
            self.set_enabled_categories(volume_id, updated_ids)

    # ---------------------------
    # Downloads (ZIP/CSV)
    # ---------------------------
    def request_zip_download(self, volume_id: int) -> ProcessingTask:
        """Request async ZIP generation for a volume. This task sends an email when complete."""
        payload = self._get_json(f"/volumes/{volume_id}/download-link/")
        return ProcessingTask.model_validate(payload)

    def request_csv_download(self, volume_id: int) -> ProcessingTask:
        """Request async CSV generation for a volume. This task sends an email when complete."""
        payload = self._get_json(f"/volumes/{volume_id}/csv-download-link/")
        return ProcessingTask.model_validate(payload)
