"""Sessions resource for Databrary API (read-only)."""

from __future__ import annotations

from typing import Iterator

from ..models import Page, Session
from ..models.downloads import FileDownloadLink, ProcessingTask
from ..models.files import File as FileModel
from ._base import BaseResource


class SessionsResource(BaseResource):
    """Read-only operations for sessions and their files."""

    def page(
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
    ) -> Iterator[Session]:
        """Iterate sessions within a volume across pages yielding `Session` objects."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self.paginate_items(
            f"/volumes/{volume_id}/sessions/",
            params=params,
            parser=Session.model_validate,
        )

    def retrieve(self, volume_id: int, session_id: int) -> Session:
        """Retrieve a single session by id within a volume."""
        data = self._get_json(f"/volumes/{volume_id}/sessions/{session_id}/")
        return Session.model_validate(data)

    # Files under a session (read-only)
    def files_page(
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

    def files_list(
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
    ) -> Iterator[FileModel]:
        """Iterate files within a session across pages yielding `FileModel` objects."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self.paginate_items(
            f"/volumes/{volume_id}/sessions/{session_id}/files/",
            params=params,
            parser=FileModel.model_validate,
        )

    def get_file(self, volume_id: int, session_id: int, file_id: int) -> FileModel:
        """Retrieve a single file within a session."""
        data = self._get_json(f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/")
        return FileModel.model_validate(data)

    # ---------------------------
    # Downloads
    # ---------------------------
    def get_file_download_link(
        self, volume_id: int, session_id: int, file_id: int
    ) -> FileDownloadLink:
        """Request a signed link for a file download."""
        payload = self._get_json(
            f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/download-link/"
        )
        return FileDownloadLink.model_validate(payload)

    def download_file(
        self,
        volume_id: int,
        session_id: int,
        file_id: int,
        *,
        dest_path: str | None = None,
    ) -> bytes | str:
        """Download a file; returns bytes or saves to dest_path.

        If dest_path is provided, streams to file and returns the full path.
        """
        link = self.get_file_download_link(volume_id, session_id, file_id)
        url = link.download_url
        if dest_path is None:
            return self._download_bytes(url)
        return self._download_to_path(url, dest_path)

    def request_zip_download(self, volume_id: int, session_id: int) -> ProcessingTask:
        """Request async ZIP generation for a session."""
        payload = self._get_json(f"/volumes/{volume_id}/sessions/{session_id}/download-link/")
        return ProcessingTask.model_validate(payload)

    def request_csv_download(self, volume_id: int, session_id: int) -> ProcessingTask:
        """Request async CSV generation for a session."""
        payload = self._get_json(f"/volumes/{volume_id}/sessions/{session_id}/csv-download-link/")
        return ProcessingTask.model_validate(payload)
