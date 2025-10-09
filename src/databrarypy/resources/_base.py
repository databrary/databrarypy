"""Base resource providing shared HTTP and normalization helpers."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Callable as TypingCallable
from typing import Any, TypeVar

import httpx

from ..models import Page

T = TypeVar("T")


class BaseResource:
    """Common functionality shared by resource classes."""

    def __init__(
        self,
        http: httpx.Client,
        headers_fn: Callable[[], dict[str, str]],
        normalize_json: Callable[[Any], Any],
    ) -> None:
        self._normalize = normalize_json
        self._http = http
        self._headers = headers_fn

    @staticmethod
    def build_params(**kwargs: Any) -> dict[str, Any]:
        """Build query params dict by dropping None and lowercasing booleans."""
        params: dict[str, Any] = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, bool):
                params[key] = str(value).lower()
            else:
                params[key] = value
        return params

    def _raw_get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Perform GET and return parsed JSON with status validation (no normalization)."""
        resp = self._http.get(path, params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def _get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        data: Any = self._raw_get_json(path, params=params)
        return self._normalize(data)

    def _get_bytes_or_empty(self, path: str) -> bytes:
        """GET a binary endpoint; return empty bytes if 404 else content."""
        resp = self._http.get(path, headers=self._headers())
        if resp.status_code == 404:
            return b""
        resp.raise_for_status()
        return resp.content

    def _get_page(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        parser: TypingCallable[[Any], T] | None = None,
    ) -> Page[T]:
        data = self._get_json(path, params=params)
        if parser is not None:
            data["results"] = [parser(item) for item in data.get("results", [])]
        return Page[T].model_validate(data)
