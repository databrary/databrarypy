"""Folders resource for Databrary API."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Iterator, List

from ..models import Page
from ..models.bulk import BulkResult
from ..models.downloads import FileDownloadLink, ProcessingTask
from ..models.files import File as FileModel
from ..models.folders import Folder, FolderDuplicateFileCheckItem, FolderMutation
from ..utils.strings import require_nonempty_stripped
from ._base import BaseResource
from .bulk import _bulk_apply


class FoldersResource(BaseResource):
    """CRUD operations for folders, plus folder file listings and downloads."""

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
    ) -> Iterator[Folder]:
        """Iterate folders within a volume across pages yielding `Folder` objects."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self.paginate_items(
            f"/volumes/{volume_id}/folders/",
            params=params,
            parser=Folder.model_validate,
        )

    def retrieve(self, volume_id: int, folder_id: int) -> Folder:
        """Retrieve a single folder by id within a volume."""
        data = self._get_json(f"/volumes/{volume_id}/folders/{folder_id}/")
        return Folder.model_validate(data)

    # Files under a folder (read-only)
    def files_page(
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

    def files_list(
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
    ) -> Iterator[FileModel]:
        """Iterate files within a folder across pages yielding `FileModel` objects."""
        params = self.build_params(
            search=search,
            date_from=date_from,
            date_to=date_to,
            release_level=release_level,
            page=page,
            page_size=page_size,
        )
        return self.paginate_items(
            f"/volumes/{volume_id}/folders/{folder_id}/files/",
            params=params,
            parser=FileModel.model_validate,
        )

    def get_file(self, volume_id: int, folder_id: int, file_id: int) -> FileModel:
        """Retrieve a single file within a folder."""
        data = self._get_json(f"/volumes/{volume_id}/folders/{folder_id}/files/{file_id}/")
        return FileModel.model_validate(data)

    # ---------------------------
    # Downloads
    # ---------------------------
    def get_file_download_link(
        self, volume_id: int, folder_id: int, file_id: int
    ) -> FileDownloadLink:
        """Request a signed link for a folder file download."""
        payload = self._get_json(
            f"/volumes/{volume_id}/folders/{folder_id}/files/{file_id}/download-link/"
        )
        return FileDownloadLink.model_validate(payload)

    def download_file(
        self,
        volume_id: int,
        folder_id: int,
        file_id: int,
        *,
        dest_path: str | None = None,
    ) -> bytes | str:
        """Download a folder file; returns bytes or saves to dest_path."""
        link = self.get_file_download_link(volume_id, folder_id, file_id)
        url = link.download_url
        if dest_path is None:
            return self._download_bytes(url)
        return self._download_to_path(url, dest_path)

    def request_zip_download(self, volume_id: int, folder_id: int) -> ProcessingTask:
        """Request async ZIP generation for a folder."""
        payload = self._get_json(f"/volumes/{volume_id}/folders/{folder_id}/download-link/")
        return ProcessingTask.model_validate(payload)

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
    ) -> FolderMutation:
        """Create a folder in a volume. ``name`` is required and non-empty."""
        body: dict[str, Any] = {"name": require_nonempty_stripped(name, field="name")}
        if release_level is not None:
            body["release_level"] = release_level
        if source_date is not None:
            body["source_date"] = source_date
        data = self._post_json(f"/volumes/{volume_id}/folders/", json=body)
        return FolderMutation.model_validate(data)

    def update(
        self,
        volume_id: int,
        folder_id: int,
        *,
        name: str,
        release_level: str | None = None,
        source_date: str | None = None,
    ) -> FolderMutation:
        """Full update (PUT) of a folder. ``name`` is required.

        Optional fields are omitted from the request body when ``None`` so the
        server can retain existing values instead of receiving JSON ``null``.
        """
        body: dict[str, Any] = {"name": require_nonempty_stripped(name, field="name")}
        if release_level is not None:
            body["release_level"] = release_level
        if source_date is not None:
            body["source_date"] = source_date
        data = self._put_json(f"/volumes/{volume_id}/folders/{folder_id}/", json=body)
        return FolderMutation.model_validate(data)

    def patch(
        self,
        volume_id: int,
        folder_id: int,
        *,
        name: str | None = None,
        release_level: str | None = None,
        source_date: str | None = None,
    ) -> FolderMutation:
        """Partial update (PATCH) of a folder. Only provided fields are sent."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = require_nonempty_stripped(name, field="name")
        if release_level is not None:
            body["release_level"] = release_level
        if source_date is not None:
            body["source_date"] = source_date
        if not body:
            raise ValueError("At least one of name, release_level, or source_date must be provided")
        data = self._patch_json(f"/volumes/{volume_id}/folders/{folder_id}/", json=body)
        return FolderMutation.model_validate(data)

    def delete(self, volume_id: int, folder_id: int) -> bool:
        """Soft-delete a folder."""
        return self._delete_request(f"/volumes/{volume_id}/folders/{folder_id}/")

    def check_duplicate_files(
        self,
        volume_id: int,
        folder_id: int,
        filenames: List[str],
    ) -> List[FolderDuplicateFileCheckItem]:
        """Return one row per filename with duplicate presence flags."""
        data = self._post_json(
            f"/volumes/{volume_id}/folders/{folder_id}/check-duplicate-files/",
            json={"filenames": filenames},
        )
        if not isinstance(data, list):
            raise ValueError(
                "check_duplicate_files expected a JSON array from the server; "
                f"got {type(data).__name__}"
            )
        return [FolderDuplicateFileCheckItem.model_validate(item) for item in data]

    # ---------------------------
    # File metadata (PUT/PATCH/DELETE on nested files)
    # ---------------------------
    def update_file(
        self,
        volume_id: int,
        folder_id: int,
        file_id: int,
        *,
        name: str,
        release_level: str | None = None,
        source_date: str | None = None,
        date: dict[str, Any] | None = None,
        date_precision: str | None = None,
        is_estimated: bool | None = None,
    ) -> FileModel:
        """Full PUT update of a folder file. ``name`` is required.

        Only ``name`` and ``release_level`` are sent on the wire (and only
        those are honored server-side). Other keyword arguments are accepted
        for symmetry with session file APIs but are not included in the request.
        """
        _ = (source_date, date, date_precision, is_estimated)
        payload: dict[str, Any] = {"name": require_nonempty_stripped(name, field="name")}
        if release_level is not None:
            payload["release_level"] = release_level
        data = self._put_json(
            f"/volumes/{volume_id}/folders/{folder_id}/files/{file_id}/",
            json=payload,
        )
        return FileModel.model_validate(data)

    def patch_file(
        self,
        volume_id: int,
        folder_id: int,
        file_id: int,
        *,
        name: str | None = None,
        release_level: str | None = None,
        source_date: str | None = None,
        date: dict[str, Any] | None = None,
        date_precision: str | None = None,
        is_estimated: bool | None = None,
    ) -> FileModel:
        """Partial PATCH update of a folder file.

        Only ``name`` and ``release_level`` are sent; other keyword arguments
        are ignored (folder writes use ``FileSerializer``, which does not honor
        session-only file fields).
        """
        _ = (source_date, date, date_precision, is_estimated)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = require_nonempty_stripped(name, field="name")
        if release_level is not None:
            payload["release_level"] = release_level
        if not payload:
            raise ValueError("At least one writable field must be provided")
        data = self._patch_json(
            f"/volumes/{volume_id}/folders/{folder_id}/files/{file_id}/",
            json=payload,
        )
        return FileModel.model_validate(data)

    def delete_file(self, volume_id: int, folder_id: int, file_id: int) -> bool:
        """Soft-delete a file from a folder."""
        return self._delete_request(f"/volumes/{volume_id}/folders/{folder_id}/files/{file_id}/")

    # ---------------------------
    # Bulk operations
    # ---------------------------
    def bulk_delete(self, volume_id: int, folder_ids: Iterable[int]) -> BulkResult:
        """Soft-delete multiple folders sequentially. Fast-fails with partial state."""
        return _bulk_apply(
            inputs=list(folder_ids),
            fn=lambda fid: self.delete(volume_id, fid),
            is_failure=lambda res: res is not True,
        )

    def bulk_create(self, volume_id: int, items: Iterable[dict[str, Any]]) -> BulkResult:
        """Create multiple folders.

        Each mapping is passed as keyword arguments to :meth:`create`.
        """
        return _bulk_apply(
            inputs=list(items),
            fn=lambda item: self.create(volume_id, **item),
        )

    def bulk_rename(
        self,
        volume_id: int,
        renames: Iterable[tuple[int, str]],
    ) -> BulkResult:
        """Rename folders via PATCH (``name`` only).

        ``renames`` are ``(folder_id, new_name)`` pairs.
        """
        return _bulk_apply(
            inputs=list(renames),
            fn=lambda pair: self.patch(volume_id, pair[0], name=pair[1]),
        )

    def bulk_delete_files(
        self,
        volume_id: int,
        folder_id: int,
        file_ids: Iterable[int],
    ) -> BulkResult:
        """Soft-delete multiple files within a folder. Fast-fails with partial state."""
        return _bulk_apply(
            inputs=list(file_ids),
            fn=lambda fid: self.delete_file(volume_id, folder_id, fid),
            is_failure=lambda res: res is not True,
        )

    def bulk_rename_files(
        self,
        volume_id: int,
        folder_id: int,
        renames: Iterable[tuple[int, str]],
    ) -> BulkResult:
        """Rename multiple files in a folder via PATCH (``name`` only).

        ``renames`` are ``(file_id, new_name)`` pairs.
        """
        return _bulk_apply(
            inputs=list(renames),
            fn=lambda pair: self.patch_file(volume_id, folder_id, pair[0], name=pair[1]),
        )
