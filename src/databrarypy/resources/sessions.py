"""Sessions resource for Databrary API."""

from __future__ import annotations

import logging
from typing import Any, Iterator, List

from ..models import Page, Session
from ..models.downloads import FileDownloadLink, ProcessingTask
from ..models.files import File as FileModel
from ..models.files import FileWrite
from ._base import BaseResource

logger = logging.getLogger(__name__)


class SessionsResource(BaseResource):
    """Operations for sessions, their files, and record-file associations."""

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

    # ---------------------------
    # Record-file associations
    # ---------------------------
    def assign_record_to_file(
        self,
        volume_id: int,
        session_id: int,
        file_id: int,
        record_id: int,
    ) -> dict[str, Any]:
        """Assign a record to a session file.

        Returns the assignment data.  Logs a warning if the record was
        already assigned to the file (server returns 200 instead of 201).
        """
        path = f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/assign-record/"
        resp = self._send_request("POST", path=path, json={"record_id": record_id})
        if resp.status_code == 200:
            logger.warning(
                "Record %d is already assigned to file %d in session %d of volume %d",
                record_id,
                file_id,
                session_id,
                volume_id,
            )
        try:
            data = resp.json()
        except Exception:
            return {}
        return self._normalize(data) if self._normalize else data  # type: ignore[return-value]

    def unassign_record_from_file(
        self,
        volume_id: int,
        session_id: int,
        file_id: int,
        record_id: int,
    ) -> dict[str, Any]:
        """Remove the association between a record and a session file."""
        path = f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/unassign-record/"
        data = self._post_json(path, json={"record_id": record_id})
        return data  # type: ignore[no-any-return]

    # ---------------------------
    # Write (CRUD)
    # ---------------------------
    def create(
        self,
        volume_id: int,
        *,
        name: str,
        release_level: str | None = None,
        source_date: str | None = None,
    ) -> Session:
        """Create a session in a volume. ``name`` is required and non-empty."""
        body: dict[str, Any] = {"name": name}
        if release_level is not None:
            body["release_level"] = release_level
        if source_date is not None:
            body["source_date"] = source_date
        data = self._post_json(f"/volumes/{volume_id}/sessions/", json=body)
        return Session.model_validate(data)

    def update(
        self,
        volume_id: int,
        session_id: int,
        *,
        name: str,
        release_level: str | None = None,
        source_date: str | None = None,
    ) -> Session:
        """Full update (PUT) of a session. ``name`` is required."""
        body: dict[str, Any] = {
            "name": name,
            "release_level": release_level,
            "source_date": source_date,
        }
        data = self._put_json(f"/volumes/{volume_id}/sessions/{session_id}/", json=body)
        return Session.model_validate(data)

    def patch(
        self,
        volume_id: int,
        session_id: int,
        *,
        name: str | None = None,
        release_level: str | None = None,
        source_date: str | None = None,
    ) -> Session:
        """Partial update (PATCH) of a session. Only provided fields are sent."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if release_level is not None:
            body["release_level"] = release_level
        if source_date is not None:
            body["source_date"] = source_date
        if not body:
            raise ValueError("At least one of name, release_level, or source_date must be provided")
        data = self._patch_json(f"/volumes/{volume_id}/sessions/{session_id}/", json=body)
        return Session.model_validate(data)

    def delete(self, volume_id: int, session_id: int) -> bool:
        """Soft-delete a session."""
        return self._delete_request(f"/volumes/{volume_id}/sessions/{session_id}/")

    # ---------------------------
    # Default records
    # ---------------------------
    def add_default_record(self, volume_id: int, session_id: int, record_id: int) -> bool:
        """Attach a record as a session default. Returns True on success."""
        self._post_json(
            f"/volumes/{volume_id}/sessions/{session_id}/add-default-record/",
            json={"record_id": record_id},
        )
        return True

    def remove_default_record(self, volume_id: int, session_id: int, record_id: int) -> bool:
        """Detach a record from session defaults. Returns True on success."""
        self._post_json(
            f"/volumes/{volume_id}/sessions/{session_id}/remove-default-record/",
            json={"record_id": record_id},
        )
        return True

    # ---------------------------
    # Duplicate file check
    # ---------------------------
    def check_duplicate_files(
        self,
        volume_id: int,
        session_id: int,
        filenames: List[str],
    ) -> List[dict[str, Any]]:
        """Return ``[{"filename": str, "exists": bool}, ...]`` for each filename."""
        data = self._post_json(
            f"/volumes/{volume_id}/sessions/{session_id}/check-duplicate-files/",
            json={"filenames": filenames},
        )
        return data if isinstance(data, list) else []

    # ---------------------------
    # File metadata (PUT/PATCH/DELETE on nested files)
    # ---------------------------
    def update_file(
        self,
        volume_id: int,
        session_id: int,
        file_id: int,
        *,
        name: str,
        release_level: str | None = None,
        source_date: str | None = None,
        date: dict[str, Any] | None = None,
        date_precision: str | None = None,
        is_estimated: bool | None = None,
    ) -> FileModel:
        """Full PUT update of a session file. ``name`` is required."""
        payload = FileWrite(
            name=name,
            release_level=release_level,
            source_date=source_date,
            date=date,
            date_precision=date_precision,
            is_estimated=is_estimated,
        ).to_payload(drop_none=False)
        data = self._put_json(
            f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/",
            json=payload,
        )
        return FileModel.model_validate(data)

    def patch_file(
        self,
        volume_id: int,
        session_id: int,
        file_id: int,
        *,
        name: str | None = None,
        release_level: str | None = None,
        source_date: str | None = None,
        date: dict[str, Any] | None = None,
        date_precision: str | None = None,
        is_estimated: bool | None = None,
    ) -> FileModel:
        """Partial PATCH update of a session file. Only provided fields are sent."""
        payload = FileWrite(
            name=name,
            release_level=release_level,
            source_date=source_date,
            date=date,
            date_precision=date_precision,
            is_estimated=is_estimated,
        ).to_payload(drop_none=True)
        if not payload:
            raise ValueError("At least one writable field must be provided")
        data = self._patch_json(
            f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/",
            json=payload,
        )
        return FileModel.model_validate(data)

    def delete_file(self, volume_id: int, session_id: int, file_id: int) -> bool:
        """Soft-delete a file from a session."""
        return self._delete_request(f"/volumes/{volume_id}/sessions/{session_id}/files/{file_id}/")
