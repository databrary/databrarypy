"""Unit tests for bulk operation engine (_bulk_apply, resume_bulk)."""

from __future__ import annotations

import pytest

from databrarypy.models.bulk import BulkItem, BulkItemStatus, BulkOperationError, BulkResult
from databrarypy.resources.bulk import _bulk_apply, resume_bulk


def test_bulk_apply_success():
    result = _bulk_apply(inputs=[1, 2, 3], fn=lambda x: x * 2)
    assert len(result.succeeded) == 3
    assert [item.result for item in result.succeeded] == [2, 4, 6]


def test_bulk_apply_raises_on_exception_with_partial_state():
    def fn(x: int) -> int:
        if x == 2:
            raise ValueError("boom")
        return x

    with pytest.raises(BulkOperationError, match="Bulk operation failed") as exc_info:
        _bulk_apply(inputs=[1, 2, 3], fn=fn)

    partial = exc_info.value.partial
    assert len(partial.succeeded) == 1
    assert partial.succeeded[0].input == 1
    assert partial.failed[0].input == 2
    assert partial.pending[0].input == 3


def test_bulk_apply_is_failure_callback():
    with pytest.raises(BulkOperationError, match="failure value"):
        _bulk_apply(
            inputs=[True, False],
            fn=lambda x: x,
            is_failure=lambda res: res is False,
        )


def test_bulk_apply_preflight_skips_items():
    def preflight(state: BulkResult) -> BulkResult:
        state.items[1].status = BulkItemStatus.SKIPPED
        state.items[1].reason = "duplicate"
        return state

    result = _bulk_apply(inputs=["a", "b", "c"], fn=lambda x: x.upper(), preflight=preflight)
    assert len(result.succeeded) == 2
    assert len(result.skipped) == 1
    assert result.skipped[0].input == "b"


def test_resume_bulk_splices_results():
    partial = BulkResult(
        items=[
            BulkItem(input=1, status=BulkItemStatus.SUCCESS, result="ok"),
            BulkItem(input=2, status=BulkItemStatus.FAILED, error="err"),
            BulkItem(input=3, status=BulkItemStatus.PENDING),
        ]
    )

    def redo_fn(inputs: list[int]) -> BulkResult:
        return BulkResult(
            items=[
                BulkItem(input=inp, status=BulkItemStatus.SUCCESS, result=inp * 10)
                for inp in inputs
            ]
        )

    resumed = resume_bulk(partial, redo_fn)
    assert resumed.items[0].result == "ok"
    assert resumed.items[1].result == 20
    assert resumed.items[2].result == 30


def test_resume_bulk_noop_when_nothing_to_redo():
    partial = BulkResult(items=[BulkItem(input=1, status=BulkItemStatus.SUCCESS, result=1)])

    def should_not_run(_inputs: list[int]) -> BulkResult:
        raise AssertionError("fn should not be called")

    assert resume_bulk(partial, should_not_run) is partial


def test_resume_bulk_length_mismatch_raises():
    partial = BulkResult(
        items=[
            BulkItem(input=1, status=BulkItemStatus.FAILED),
            BulkItem(input=2, status=BulkItemStatus.PENDING),
        ]
    )

    def bad_fn(_inputs: list[int]) -> BulkResult:
        return BulkResult(items=[BulkItem(input=1, status=BulkItemStatus.SUCCESS)])

    with pytest.raises(ValueError, match="different number of items"):
        resume_bulk(partial, bad_fn)
