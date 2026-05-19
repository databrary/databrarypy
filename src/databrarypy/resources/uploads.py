"""Uploads resource: three-step upload pipeline (initiate / PUT bytes / complete)."""

from __future__ import annotations

import logging
import mimetypes
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, Literal

from pydantic import TypeAdapter

from ..errors import ApiError
from ..models.bulk import BulkItemStatus, BulkResult
from ..models.uploads import (
    TERMINAL_FAILURE_STATUSES,
    InitiateMultipartResponse,
    InitiateResponse,
    InitiateSingleResponse,
    Part,
    PartUrl,
    UploadResult,
    UploadStatus,
)
from ._base import BaseResource
from .bulk import _bulk_apply

logger = logging.getLogger(__name__)

_INITIATE_ADAPTER: TypeAdapter[InitiateResponse] = TypeAdapter(InitiateResponse)


class UploadsResource(BaseResource):
    """Upload pipeline operations for sessions and folders.

    Three-step flow:
      1. :meth:`initiate` — register the upload, receive a signed upload URL.
      2. PUT bytes directly to the storage backend (Nginx on on-prem, S3 on cloud).
      3. :meth:`complete` — finalize multipart uploads on cloud only (no-op for single).

    Use :meth:`upload_file` for the full orchestrated flow.

    Presigned PUT requests use the raw HTTP client and do **not** use the client's
    authenticated-API retry/backoff. Callers may retry at a higher level if needed.

    Multipart uploads that fail before a successful :meth:`complete` trigger a best-effort
    :meth:`abort_multipart` to reduce orphaned MPU state on the server (cloud only).
    """

    # Reference values matching databrary-ai (UploadToAWSService); not used for branching —
    # the API decides single vs multipart from ``file_size`` in :meth:`initiate`.
    MULTIPART_THRESHOLD_BYTES = 100 * 1024 * 1024
    MULTIPART_PART_SIZE_BYTES = 10 * 1024 * 1024

    # ---------------------------
    # Low-level pipeline
    # ---------------------------
    def initiate(
        self,
        *,
        filename: str,
        destination_type: str,
        object_id: int,
        file_size: int | None = None,
        content_type: str | None = None,
        source_session_id: int | None = None,
        source_folder_id: int | None = None,
    ) -> InitiateResponse:
        """Register an upload and obtain presigned URL(s)."""
        body: dict[str, Any] = {
            "filename": filename,
            "destination_type": destination_type,
            "object_id": object_id,
        }
        if file_size is not None:
            body["file_size"] = file_size
        if content_type is not None:
            body["content_type"] = content_type
        if source_session_id is not None:
            body["source_session_id"] = source_session_id
        if source_folder_id is not None:
            body["source_folder_id"] = source_folder_id

        data = self._post_json("/uploads/initiate/", json=body)
        if isinstance(data, dict) and "upload_type" not in data:
            # Plain databrary-core returns {signed_upload_url, status_url} with no
            # upload_type; treat as single so the discriminated union resolves.
            data["upload_type"] = "single"
        return _INITIATE_ADAPTER.validate_python(data)

    def status(self, upload_guid: str) -> str:
        """Return the raw ``status`` string from ``/uploads/{upload_guid}/status/``.

        Unlike :meth:`upload_file`'s internal polling, this method is strict: a non-object
        JSON body raises :exc:`~databrarypy.errors.ApiError` instead of being treated as
        an empty status.
        """
        data = self._get_json(f"/uploads/{upload_guid}/status/")
        if not isinstance(data, dict):
            raise ApiError("Unexpected status response shape")
        return str(data.get("status", ""))

    def complete(
        self,
        upload_guid: str,
        *,
        s3_upload_id: str,
        parts: list[Part] | list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Complete a multipart upload (AI / multipart-only endpoint).

        Only call for multipart uploads. Single uploads do not have a
        completion step — the server reacts to the S3 ``ObjectCreated`` event.
        """
        normalised: list[dict[str, Any]] = [
            p.model_dump() if isinstance(p, Part) else dict(p) for p in parts
        ]
        data = self._post_json(
            "/uploads/complete-multipart/",
            json={
                "upload_guid": upload_guid,
                "s3_upload_id": s3_upload_id,
                "parts": normalised,
            },
        )
        if not isinstance(data, dict):
            raise ApiError("Unexpected response shape from complete-multipart endpoint")
        return data

    def presign_parts(
        self,
        upload_guid: str,
        s3_upload_id: str,
        part_numbers: list[int],
    ) -> list[PartUrl]:
        """Generate fresh presigned URLs for specific multipart parts (AI / cloud-only).

        Not available on on-prem (``backend_2.0``).  :meth:`upload_file` does not refresh
        expired URLs; for very long uploads or custom flows, obtain new URLs here and PUT
        parts yourself.
        """
        data = self._post_json(
            "/uploads/presign-parts/",
            json={
                "upload_guid": upload_guid,
                "s3_upload_id": s3_upload_id,
                "part_numbers": part_numbers,
            },
        )
        if not isinstance(data, dict):
            raise ApiError("Unexpected response shape from presign-parts endpoint")
        urls = data.get("part_urls", [])
        return [PartUrl.model_validate(u) for u in urls]

    def abort_multipart(self, upload_guid: str, s3_upload_id: str) -> None:
        """Abort an in-progress multipart upload and mark it failed server-side (AI / cloud-only).

        Not available on on-prem (``backend_2.0``).  Raises on HTTP error; returns ``None``
        on success.
        """
        self._send_request(
            "POST",
            path="/uploads/abort-multipart/",
            json={"upload_guid": upload_guid, "s3_upload_id": s3_upload_id},
        )

    # ---------------------------
    # High-level orchestration
    # ---------------------------
    def upload_file(
        self,
        path: str | Path,
        *,
        destination_type: str,
        object_id: int,
        content_type: str | None = None,
        source_session_id: int | None = None,
        source_folder_id: int | None = None,
        poll_status: bool = True,
        poll_interval: float = 2.0,
        poll_timeout: float = 600.0,
    ) -> UploadResult:
        """End-to-end upload: initiate → PUT bytes → (multipart only) complete → poll.

        Works for both sessions (``destination_type="session"``) and folders
        (``destination_type="folder"``). Branches automatically on the server's
        ``upload_type`` response (single vs multipart).

        Args:
            path: Local file path to upload.
            destination_type: ``"session"`` or ``"folder"`` (API convention).
            object_id: Destination session or folder id.
            content_type: Optional override; when omitted, guessed from the filename.
            source_session_id: Required when ``destination_type`` is
                ``"linked_volume_session"``.
            source_folder_id: Required when ``destination_type`` is
                ``"linked_volume_folder"``.
            poll_status: When True, poll ``status_url`` until a terminal status or timeout.
            poll_interval: Seconds between status polls. Use ``0.0`` only in tests;
                production callers should use at least ``1.0`` to avoid hammering the API.
            poll_timeout: Maximum seconds to wait before returning the last-known status.

        Note:
            Polling stops on ``completed`` or on strings in ``TERMINAL_FAILURE_STATUSES``
            (see ``databrarypy.models.uploads``). Add new terminal failure values there when
            the API introduces them, or polling continues until ``poll_timeout``.

            Single/multipart PUTs to presigned S3 URLs do not use the client's API retry
            policy (see class docstring). Multipart failures invoke :meth:`abort_multipart`
            before propagating the error when finalize was not reached.
        """
        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Upload source not found: {file_path}")

        file_size = file_path.stat().st_size
        resolved_ct = content_type or mimetypes.guess_type(file_path.name)[0]

        response = self.initiate(
            filename=file_path.name,
            destination_type=destination_type,
            object_id=object_id,
            file_size=file_size,
            content_type=resolved_ct,
            source_session_id=source_session_id,
            source_folder_id=source_folder_id,
        )

        upload_type: Literal["single", "multipart"]
        if isinstance(response, InitiateMultipartResponse):
            self._upload_multipart(file_path, response)
            upload_guid: str | None = response.upload_guid
            upload_type = "multipart"
        else:
            assert isinstance(response, InitiateSingleResponse)
            self._upload_single(file_path, response)
            upload_guid = response.upload_guid
            upload_type = "single"

        final_status = (
            self._poll_until_terminal(response.status_url, poll_interval, poll_timeout)
            if poll_status
            else ""
        )

        return UploadResult(
            upload_guid=upload_guid,
            upload_type=upload_type,
            final_status=final_status,
            status_url=response.status_url,
        )

    # ---------------------------
    # Internals
    # ---------------------------
    def _upload_single(self, file_path: Path, response: InitiateSingleResponse) -> None:
        with file_path.open("rb") as fh:
            resp = self._http.put(
                response.signed_upload_url,
                content=fh,
                headers=response.required_headers or {},
            )
            resp.raise_for_status()

    def _try_abort_multipart(self, upload_guid: str, s3_upload_id: str) -> None:
        try:
            self.abort_multipart(upload_guid, s3_upload_id)
        except Exception:
            logger.warning(
                "abort_multipart failed for upload_guid=%r (cleanup may be needed)",
                upload_guid,
                exc_info=True,
            )

    def _upload_multipart(self, file_path: Path, response: InitiateMultipartResponse) -> None:
        finalized = False
        try:
            parts: list[Part] = []
            with file_path.open("rb") as fh:
                for part_url in sorted(response.part_urls, key=lambda p: p.part_number):
                    chunk = fh.read(response.part_size)
                    if not chunk:
                        break
                    put_resp = self._http.put(part_url.url, content=chunk)
                    put_resp.raise_for_status()
                    etag = put_resp.headers.get("ETag") or put_resp.headers.get("etag", "")
                    parts.append(Part(part_number=part_url.part_number, etag=etag.strip('"')))

                if fh.read(1):
                    raise ValueError(
                        "File has more data than the server-provided part URLs can cover; "
                        "the upload was aborted to avoid incomplete data."
                    )

            self.complete(
                response.upload_guid,
                s3_upload_id=response.s3_upload_id,
                parts=parts,
            )
            finalized = True
        except BaseException:
            if not finalized:
                self._try_abort_multipart(response.upload_guid, response.s3_upload_id)
            raise

    # ---------------------------
    # Bulk upload
    # ---------------------------
    def bulk_upload_files(
        self,
        file_paths: Iterable[str | Path],
        *,
        destination_type: str,
        object_id: int,
        volume_id: int,
        preflight: bool = True,
        content_type: str | None = None,
        poll_status: bool = True,
        poll_interval: float = 2.0,
        poll_timeout: float = 600.0,
    ) -> BulkResult:
        """Upload many files to a single session or folder, fast-failing on the first error.

        With ``preflight=True`` (default), the matching ``check_duplicate_files``
        endpoint is called first; any file whose basename already exists in the
        target container is marked ``skipped`` with ``reason="duplicate"`` and
        not uploaded.

        ``destination_type`` must be ``"session"`` or ``"folder"``.
        """
        if destination_type not in {"session", "folder"}:
            raise ValueError(
                f"destination_type must be 'session' or 'folder', got {destination_type!r}"
            )

        paths = [Path(p) for p in file_paths]

        preflight_fn = (
            self._make_duplicate_preflight(volume_id, destination_type, object_id)
            if preflight
            else None
        )

        def _upload_one(path: Path) -> UploadResult:
            return self.upload_file(
                path,
                destination_type=destination_type,
                object_id=object_id,
                content_type=content_type,
                poll_status=poll_status,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
            )

        return _bulk_apply(inputs=paths, fn=_upload_one, preflight=preflight_fn)

    def _make_duplicate_preflight(
        self,
        volume_id: int,
        destination_type: str,
        object_id: int,
    ) -> Callable[[BulkResult], BulkResult]:
        """Build a preflight that marks duplicate-filename inputs as skipped."""
        if destination_type == "session":
            endpoint = f"/volumes/{volume_id}/sessions/{object_id}/check-duplicate-files/"
        else:
            endpoint = f"/volumes/{volume_id}/folders/{object_id}/check-duplicate-files/"

        def _preflight(state: BulkResult) -> BulkResult:
            filenames = [Path(item.input).name for item in state.items]
            data = self._post_json(endpoint, json={"filenames": filenames})
            if not isinstance(data, list):
                return state
            exists_by_name: dict[str, bool] = {}
            for row in data:
                if not isinstance(row, dict):
                    continue
                fname = row.get("filename")
                if isinstance(fname, str):
                    exists_by_name[fname] = bool(row.get("exists"))
            for item, name in zip(state.items, filenames, strict=True):
                if exists_by_name.get(name):
                    item.status = BulkItemStatus.SKIPPED
                    item.reason = "duplicate"
            return state

        return _preflight

    def _poll_until_terminal(
        self,
        status_url: str,
        poll_interval: float,
        poll_timeout: float,
    ) -> str:
        """Poll ``status_url`` until a terminal status is reached or timeout."""
        deadline = time.monotonic() + poll_timeout
        last_status = ""
        while True:
            resp = self._http.get(status_url, headers=self._headers())
            resp.raise_for_status()
            payload = resp.json() if resp.content else {}
            last_status = str(payload.get("status", "")) if isinstance(payload, dict) else ""
            if (
                last_status == UploadStatus.COMPLETED.value
                or last_status in TERMINAL_FAILURE_STATUSES
            ):
                return last_status
            if time.monotonic() >= deadline:
                logger.warning(
                    "Upload status polling timed out after %.0fs (last status: %r)",
                    poll_timeout,
                    last_status,
                )
                return last_status
            time.sleep(poll_interval)
