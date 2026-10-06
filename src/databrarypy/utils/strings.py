"""String normalization helpers for client-side validation."""

from __future__ import annotations


def require_nonempty_stripped(text: str, *, field: str) -> str:
    """Strip *text* and return it, or raise if nothing remains.

    Args:
        text: Input string (may be surrounded by whitespace).
        field: Logical field name used in the ``ValueError`` message.

    Raises:
        ValueError: If the stripped string is empty.
    """
    stripped = text.strip()
    if not stripped:
        raise ValueError(f"{field} must be a non-empty string")
    return stripped
