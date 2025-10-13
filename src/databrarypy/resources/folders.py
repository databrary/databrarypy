"""Folders resource for Databrary API (read-only)."""

from __future__ import annotations

from ..models import Page
from ..models.files import File as FileModel
from ..models.folders import Folder
from ._base import BaseResource


class FoldersResource(BaseResource):
    """Read-only operations for folders and their files."""

    def list(
        self,
        volume_id: int,
        *,
        search: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        release_level: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[Folder]:
        """List folders within a volume (paginated)."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self._get_page(
            f"/volumes/{volume_id}/folders/",
            params=params,
            parser=Folder.model_validate,
        )

    def retrieve(self, volume_id: int, folder_id: int) -> Folder:
        """Retrieve a single folder by id within a volume."""
        data = self._get_json(f"/volumes/{volume_id}/folders/{folder_id}/")
        return Folder.model_validate(data)

    # Files under a folder (read-only)
    def files(
        self,
        volume_id: int,
        folder_id: int,
        *,
        search: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        release_level: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[FileModel]:
        """List files within a folder (paginated)."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self._get_page(
            f"/volumes/{volume_id}/folders/{folder_id}/files/",
            params=params,
            parser=FileModel.model_validate,
        )

    def get_file(self, volume_id: int, folder_id: int, file_id: int) -> FileModel:
        """Retrieve a single file within a folder."""
        data = self._get_json(f"/volumes/{volume_id}/folders/{folder_id}/files/{file_id}/")
        return FileModel.model_validate(data)
