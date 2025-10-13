"""Volumes resource for Databrary API."""

from __future__ import annotations

import builtins
from typing import Any

from ..models import (
    Page,
    VolumeActivityItem,
    VolumeCollaborator,
    VolumeDetail,
    VolumeLink,
    VolumeListItem,
)
from ..models.downloads import ProcessingTask
from ._base import BaseResource


class VolumesResource(BaseResource):
    """Resource for volume operations and relations (excluding sessions/downloads)."""

    def list(
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

    def fundings(self, volume_id: int) -> builtins.list[dict[str, Any]]:
        """List volume fundings (nested funder objects)."""
        # Backend returns list of VolumeFundingSerializer; we parse nested on VolumeDetail
        data = self._get_json(f"/volumes/{volume_id}/fundings/")
        return list(data)

    def collaborators(self, volume_id: int) -> builtins.list[VolumeCollaborator]:
        """List collaborators visible to the current user for the volume."""
        data = self._get_json(f"/volumes/{volume_id}/collaborators/")
        return [VolumeCollaborator.model_validate(item) for item in data]

    def collaborator(self, volume_id: int, collaborator_id: int) -> VolumeCollaborator:
        """Retrieve a specific collaborator by id."""
        data = self._get_json(f"/volumes/{volume_id}/collaborators/{collaborator_id}/")
        return VolumeCollaborator.model_validate(data)

    # Activity/history
    def activity(
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

    # ---------------------------
    # Downloads (ZIP/CSV)
    # ---------------------------
    def request_zip_download(self, volume_id: int) -> ProcessingTask:
        """Request async ZIP generation for a volume."""
        payload = self._get_json(f"/volumes/{volume_id}/download-link/")
        return ProcessingTask.model_validate(payload)

    def request_csv_download(self, volume_id: int) -> ProcessingTask:
        """Request async CSV generation for a volume."""
        payload = self._get_json(f"/volumes/{volume_id}/csv-download-link/")
        return ProcessingTask.model_validate(payload)
