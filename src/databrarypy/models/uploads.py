"""Models for the upload pipeline (initiate / status / complete)."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class UploadStatus(StrEnum):
    """Upload status values returned by the status endpoint.

    On-prem (databrary-core / backend_2.0): ``initiated``, ``processing``, ``completed``,
    ``failed``.  AI (databrary-ai): ``scanning``, ``completed``, ``infected``,
    ``upload_failed``, ``processing_failed``.

    ``INITIATED``, ``PROCESSING``, and ``SCANNING`` are non-terminal during polling.
    ``COMPLETED`` and strings in ``TERMINAL_FAILURE_STATUSES`` end polling when matched.
    """

    # on-prem (databrary-core / backend_2.0) statuses
    INITIATED = "initiated"
    PROCESSING = "processing"
    FAILED = "failed"
    # shared terminal success
    COMPLETED = "completed"
    # AI (databrary-ai) statuses
    SCANNING = "scanning"
    INFECTED = "infected"
    UPLOAD_FAILED = "upload_failed"
    PROCESSING_FAILED = "processing_failed"


# Failure strings that stop upload status polling immediately (besides ``completed``).
# When the API adds a new terminal failure value, extend UploadStatus and add its
# ``.value`` here; otherwise ``UploadsResource.upload_file`` polls until timeout.
TERMINAL_FAILURE_STATUSES = frozenset(
    {
        UploadStatus.FAILED.value,  # on-prem
        UploadStatus.INFECTED.value,  # AI
        UploadStatus.UPLOAD_FAILED.value,  # AI
        UploadStatus.PROCESSING_FAILED.value,  # AI
    }
)


class PartUrl(BaseModel):
    """Presigned URL for a single multipart upload part."""

    part_number: int
    url: str

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Part(BaseModel):
    """Part identifier + ETag returned by S3 after a successful part PUT."""

    part_number: int
    etag: str

    model_config = {"populate_by_name": True, "extra": "ignore"}


class InitiateSingleResponse(BaseModel):
    """Response from ``/uploads/initiate/`` for small (single PUT) uploads.

    The ``upload_type`` discriminator is absent when talking to plain
    databrary-core (no multipart override); defaults to ``"single"`` in that case.
    ``required_headers`` is empty for core; AI override sets SSE-KMS / metadata headers.
    """

    upload_type: Literal["single"] = "single"
    signed_upload_url: str
    status_url: str
    required_headers: dict[str, str] = Field(default_factory=dict)
    upload_guid: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class InitiateMultipartResponse(BaseModel):
    """Response from ``/uploads/initiate/`` for multipart uploads (file_size ≥ threshold)."""

    upload_type: Literal["multipart"]
    upload_guid: str
    s3_upload_id: str
    part_urls: list[PartUrl]
    part_size: int
    status_url: str

    model_config = {"populate_by_name": True, "extra": "ignore"}


InitiateResponse = Annotated[
    Union[InitiateMultipartResponse, InitiateSingleResponse],
    Field(discriminator="upload_type"),
]


class UploadResult(BaseModel):
    """Result of the high-level :meth:`UploadsResource.upload_file` orchestration."""

    upload_guid: str | None
    upload_type: Literal["single", "multipart"]
    final_status: str
    status_url: str

    model_config = {"populate_by_name": True, "extra": "ignore"}
