"""Volumes resource for Databrary API."""

from __future__ import annotations

import builtins
from typing import Any

from ..models import (
    Page,
    VolumeCollaboratorView,
    VolumeDetail,
    VolumeLink,
    VolumeListItem,
)
from ._base import BaseResource


class VolumesResource(BaseResource):
    """Resource for volume operations and relations (excluding sessions/downloads)."""

    # Core volumes endpoints
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

    # Tags
    def tags(self, volume_id: int) -> builtins.list[str]:
        """Get tag names assigned to the volume."""
        data = self._get_json(f"/volumes/{volume_id}/tags/")
        return list(data)

    # Links
    def links(self, volume_id: int) -> builtins.list[VolumeLink]:
        """List links for the volume."""
        data = self._get_json(f"/volumes/{volume_id}/links/")
        return [VolumeLink.model_validate(item) for item in data]

    # Fundings
    def fundings(self, volume_id: int) -> builtins.list[dict[str, Any]]:
        """List volume fundings (nested funder objects)."""
        # Backend returns list of VolumeFundingSerializer; we parse nested on VolumeDetail
        data = self._get_json(f"/volumes/{volume_id}/fundings/")
        return list(data)

    # Collaborators
    def list_collaborators(self, volume_id: int) -> builtins.list[VolumeCollaboratorView]:
        """List collaborators visible to the current user for the volume."""
        data = self._get_json(f"/volumes/{volume_id}/collaborators/")
        return [VolumeCollaboratorView.model_validate(item) for item in data]

    def get_collaborator(self, volume_id: int, collaborator_id: int) -> VolumeCollaboratorView:
        """Retrieve a specific collaborator (by view id)."""
        data = self._get_json(f"/volumes/{volume_id}/collaborators/{collaborator_id}/")
        return VolumeCollaboratorView.model_validate(data)
