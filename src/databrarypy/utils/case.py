"""Utilities for converting API response keys to snake_case."""

from __future__ import annotations

import re
from typing import Any

_FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
_ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")


def camel_to_snake(name: str) -> str:
    """Convert camelCase/PascalCase to snake_case."""
    s1 = _FIRST_CAP_RE.sub(r"\1_\2", name)
    return _ALL_CAP_RE.sub(r"\1_\2", s1).lower()


def snake_keys(obj: Any) -> Any:
    """Recursively convert dict keys to snake_case for JSON-like structures."""
    if isinstance(obj, dict):
        return {camel_to_snake(k): snake_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [snake_keys(item) for item in obj]
    return obj
