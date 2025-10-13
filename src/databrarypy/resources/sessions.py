"""Sessions resource for Databrary API (read-only)."""

from __future__ import annotations

from ..models import Page, Session
from ..models.files import File as FileModel
from ._base import BaseResource


class SessionsResource(BaseResource):
    """Read-only operations for sessions and their files."""

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
    ) -> Page[Session]:
        """List sessions within a volume (paginated)."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self._get_page(
            f"/volumes/{volume_id}/sessions/",
            params=params,
            parser=Session.model_validate,
        )

    def retrieve(self, volume_id: int, session_id: int) -> Session:
        """Retrieve a single session by id within a volume."""
        data = self._get_json(f"/volumes/{volume_id}/sessions/{session_id}/")
        return Session.model_validate(data)

    # Files under a session (read-only)
    def files(
        self,
        volume_id: int,
        session_id: int,
        *,
        search: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        release_level: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[FileModel]:
        """List files within a session (paginated)."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self._get_page(
            f"/volumes/{volume_id}/sessions/{session_id}/files/",
            params=params,
            parser=FileModel.model_validate,
        )

    def get_file(self, volume_id: int, session_id: int, file_id: int) -> FileModel:
        """Retrieve a single file within a session."""
        data = self._get_json(f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/")
        return FileModel.model_validate(data)
