"""Per-item result models for bulk operations (fast-fail with partial state)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class BulkItemStatus(StrEnum):
    """Lifecycle state of a single input in a bulk operation."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class BulkItem(BaseModel):
    """One row per input in a bulk operation."""

    input: Any
    status: BulkItemStatus = BulkItemStatus.PENDING
    result: Any = None
    error: str | None = None
    reason: str | None = None

    model_config = {"arbitrary_types_allowed": True}


class BulkResult(BaseModel):
    """Aggregate state of a bulk operation: one item per input, in original order."""

    items: list[BulkItem]

    model_config = {"arbitrary_types_allowed": True}

    @property
    def succeeded(self) -> list[BulkItem]:
        """Items that completed successfully."""
        return [it for it in self.items if it.status == BulkItemStatus.SUCCESS]

    @property
    def failed(self) -> list[BulkItem]:
        """Items where the operation raised or returned a failure value."""
        return [it for it in self.items if it.status == BulkItemStatus.FAILED]

    @property
    def skipped(self) -> list[BulkItem]:
        """Items skipped by a preflight check (e.g. duplicate filenames)."""
        return [it for it in self.items if it.status == BulkItemStatus.SKIPPED]

    @property
    def pending(self) -> list[BulkItem]:
        """Items not yet attempted (fast-fail aborted before reaching them)."""
        return [it for it in self.items if it.status == BulkItemStatus.PENDING]

    def to_redo(self) -> list[Any]:
        """Inputs to retry: anything still pending or previously failed."""
        return [
            it.input
            for it in self.items
            if it.status in (BulkItemStatus.PENDING, BulkItemStatus.FAILED)
        ]


class BulkOperationError(Exception):
    """Raised on first failure during a bulk operation.

    Carries the partial :class:`BulkResult` so the caller can inspect what
    succeeded/skipped and re-run the remainder via :func:`resume_bulk`.
    """

    def __init__(self, message: str, *, partial: BulkResult, failed_input: Any) -> None:
        super().__init__(message)
        self.partial = partial
        self.failed_input = failed_input
