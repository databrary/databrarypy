"""Shared engine for bulk operations: fast-fail with partial state, plus resume."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from ..models.bulk import BulkItem, BulkItemStatus, BulkOperationError, BulkResult


def _bulk_apply(
    inputs: Iterable[Any],
    fn: Callable[[Any], Any],
    *,
    preflight: Callable[[BulkResult], BulkResult] | None = None,
    is_failure: Callable[[Any], bool] | None = None,
) -> BulkResult:
    """Run ``fn`` over each input, fast-failing on the first error.

    On failure, raises :class:`BulkOperationError` carrying the partial
    state (successes/skips already recorded, plus the failed item).
    """
    items = [BulkItem(input=inp) for inp in inputs]
    state = BulkResult(items=items)
    if preflight is not None:
        state = preflight(state)

    for item in state.items:
        if item.status != BulkItemStatus.PENDING:
            continue

        try:
            res = fn(item.input)
        except Exception as exc:
            item.status = BulkItemStatus.FAILED
            item.error = str(exc)
            raise BulkOperationError(
                f"Bulk operation failed at input {item.input!r}: {exc}",
                partial=state,
                failed_input=item.input,
            ) from exc

        if is_failure is not None and is_failure(res):
            item.status = BulkItemStatus.FAILED
            item.error = "operation returned a failure value"
            raise BulkOperationError(
                f"Bulk operation failed at input {item.input!r}: returned failure value",
                partial=state,
                failed_input=item.input,
            )

        item.status = BulkItemStatus.SUCCESS
        item.result = res

    return state


def resume_bulk(
    partial: BulkResult,
    fn: Callable[[list[Any]], BulkResult],
) -> BulkResult:
    """Re-run ``fn`` over pending+failed inputs and splice into the original order.

    ``fn`` must take the redo input list as its single argument and return
    a :class:`BulkResult`. Use ``functools.partial`` or a lambda to bind
    extra context (volume_id, destination_type, etc.).
    """
    to_redo = partial.to_redo()
    if not to_redo:
        return partial

    new_result = fn(to_redo)

    redo_indices = [
        i
        for i, item in enumerate(partial.items)
        if item.status in (BulkItemStatus.PENDING, BulkItemStatus.FAILED)
    ]
    if len(redo_indices) != len(new_result.items):
        raise ValueError("resume_bulk: fn returned a different number of items than redo inputs")

    spliced = list(partial.items)
    for k, idx in enumerate(redo_indices):
        spliced[idx] = new_result.items[k]
    return BulkResult(items=spliced)
