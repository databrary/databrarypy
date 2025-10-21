"""Base resource providing shared HTTP and normalization helpers."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Callable as TypingCallable
from contextlib import suppress
from pathlib import Path
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
        normalize_json: Callable[[object], object] | None,
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
        return self._normalize(data) if self._normalize else data

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

    # ---------------------------
    # Binary download helpers
    # ---------------------------
    def _download_bytes(self, path: str) -> bytes:
        """GET a binary endpoint; return empty bytes if 404 else content."""
        resp = self._http.get(path, headers=self._headers())
        if resp.status_code == 404:
            return b""
        resp.raise_for_status()
        return resp.content

    def _resolve_dest_path(self, resp: httpx.Response, dest_path: str | Path) -> Path:
        """Resolve final destination path. If a directory is given, use filename from headers.

        Fallback order when a directory is provided:
        1) content-disposition filename
        2) URL path basename
        3) "downloaded_file"
        """
        path = Path(dest_path)
        if path.is_dir():
            filename = "downloaded_file"
            cd = resp.headers.get("content-disposition", "")
            if "filename=" in cd:
                with suppress(Exception):
                    filename = cd.split("filename=")[-1].strip().strip('"')
            elif resp.request is not None:
                with suppress(Exception):
                    # Try to derive a sensible filename from the request URL path
                    url_path = httpx.URL(str(resp.request.url)).path
                    candidate = Path(url_path).name
                    if candidate:
                        filename = candidate
            path = path / filename
        return path

    def _download_to_path(self, url: str, dest_path: str | Path) -> str:
        """Stream a binary URL to a file and return the full saved path."""
        with self._http.stream("GET", url, headers=self._headers()) as resp:
            resp.raise_for_status()
            final_path = self._resolve_dest_path(resp, dest_path)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            with open(final_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
            return str(final_path)
