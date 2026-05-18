"""Tests for string utilities."""

import pytest

from databrarypy.utils.strings import require_nonempty_stripped


def test_require_nonempty_stripped_trims_and_returns() -> None:
    assert require_nonempty_stripped("  hello  ", field="label") == "hello"


def test_require_nonempty_stripped_rejects_blank() -> None:
    with pytest.raises(ValueError, match="title must be a non-empty string"):
        require_nonempty_stripped("   \t", field="title")
