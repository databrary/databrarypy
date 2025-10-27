"""Models for download link and processing task responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FileDownloadLink(BaseModel):
    """Response shape for file download-link endpoints."""

    download_url: str
    expires_at: datetime
    file_name: str
    file_size: int

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class ProcessingTask(BaseModel):
    """Common shape for async generation requests (ZIP/CSV)."""

    status: str
    message: str | None = None
    task_id: str | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
