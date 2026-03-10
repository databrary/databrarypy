"""Base resource providing shared HTTP and normalization helpers."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from collections.abc import Callable as TypingCallable
from contextlib import suppress
from pathlib import Path
from typing import Any, Iterator, TypeVar

import httpx

from ..errors import (
    ApiError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)
from ..models import Page

T = TypeVar("T")


class BaseResource:
    """Common functionality shared by resource classes."""

    def __init__(
        self,
        http: httpx.Client,
        headers_fn: Callable[[], dict[str, str]],
        normalize_json: Callable[[object], object] | None,
        *,
        max_retries: int = 0,
        respect_retry_after: bool = True,
        backoff_base: float = 0.5,
        backoff_jitter: float = 0.25,
    ) -> None:
        self._normalize = normalize_json
        self._http = http
        self._headers = headers_fn
        self._max_retries = max(0, int(max_retries))
        self._respect_retry_after = bool(respect_retry_after)
        self._backoff_base = float(backoff_base)
        self._backoff_jitter = float(backoff_jitter)

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

    def _send_request(
        self,
        method: str,
        *,
        path: str | None = None,
        url: str | None = None,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Response:
        """Send an HTTP request with retries/backoff and rich error mapping.

        Returns the raw ``httpx.Response`` on success (status < 400).
        Exactly one of *path* or *url* must be provided.
        """
        assert (path is None) ^ (url is None)
        target = path if path is not None else url
        assert target is not None
        attempt = 0
        while True:
            try:
                resp = self._http.request(
                    method,
                    target,
                    params=params,
                    json=json,
                    headers=self._headers(),
                    follow_redirects=True,
                )
            except httpx.HTTPError as exc:
                if attempt < self._max_retries:
                    delay = self._compute_delay(attempt)
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise ServerError(str(exc), status_code=None) from exc

            if resp.status_code < 400:
                return resp

            if resp.status_code == 401:
                raise UnauthorizedError("Unauthorized", status_code=401)
            if resp.status_code == 403:
                raise ForbiddenError("Forbidden", status_code=403)
            if resp.status_code == 404:
                raise NotFoundError("Not Found", status_code=404)

            if resp.status_code in (429, 502, 503, 504):
                retry_after_seconds: float | None = None
                if self._respect_retry_after:
                    ra = resp.headers.get("Retry-After") or resp.headers.get("retry-after")
                    if ra:
                        try:
                            retry_after_seconds = float(int(ra))
                        except Exception:
                            retry_after_seconds = None

                if attempt < self._max_retries:
                    wait = (
                        retry_after_seconds
                        if retry_after_seconds is not None
                        else self._compute_delay(attempt)
                    )
                    if wait and wait > 0:
                        time.sleep(wait)
                    attempt += 1
                    continue

                if resp.status_code == 429:
                    raise RateLimitError(
                        f"Rate limited: {resp.text}",
                        status_code=429,
                        retry_after=retry_after_seconds,
                    )
                raise ServerError(f"Server error {resp.status_code}: {resp.text}")

            if 400 <= resp.status_code < 500:
                raise ApiError(
                    f"Client error {resp.status_code}: {resp.text}", status_code=resp.status_code
                )

            if attempt < self._max_retries:
                delay = self._compute_delay(attempt)
                time.sleep(delay)
                attempt += 1
                continue
            raise ServerError(f"Server error {resp.status_code}: {resp.text}")

    def _request_json(
        self,
        *,
        path: str | None = None,
        url: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """GET JSON with retries/backoff and rich error mapping."""
        resp = self._send_request("GET", path=path, url=url, params=params)
        try:
            return resp.json()
        except Exception:
            return {}

    def _compute_delay(self, attempt: int) -> float:
        base = self._backoff_base * (2**attempt)
        jitter = random.random() * self._backoff_jitter if self._backoff_jitter > 0 else 0.0
        return float(base + jitter)

    def _raw_get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Perform GET and return parsed JSON with retries and status validation (no normalization)."""
        return self._request_json(path=path, params=params)

    def _get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        data: Any = self._raw_get_json(path, params=params)
        return self._normalize(data) if self._normalize else data

    # ---------------------------
    # Write helpers (POST / PATCH / DELETE)
    # ---------------------------
    def _post_json(
        self,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """POST JSON and return the normalised response body."""
        resp = self._send_request("POST", path=path, json=json, params=params)
        try:
            data = resp.json()
        except Exception:
            return {}
        return self._normalize(data) if self._normalize else data

    def _patch_json(self, path: str, *, json: Any | None = None) -> Any:
        """PATCH JSON and return the normalised response body."""
        resp = self._send_request("PATCH", path=path, json=json)
        try:
            data = resp.json()
        except Exception:
            return {}
        return self._normalize(data) if self._normalize else data

    def _delete_request(self, path: str) -> bool:
        """DELETE a resource. Returns ``True`` on success (2xx)."""
        self._send_request("DELETE", path=path)
        return True

    def _get_page(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        parser: TypingCallable[[Any], T] | None = None,
    ) -> Page[T]:
        data = self._get_json(path, params=params)
        if not isinstance(data, dict) or "count" not in data:
            # Normalize to an empty page structure if server returns empty body
            results = [] if not isinstance(data, dict) else data.get("results", [])
            data = {"count": len(results), "next": None, "previous": None, "results": results}
        if parser is not None:
            data["results"] = [parser(item) for item in data.get("results", [])]
        return Page[T].model_validate(data)

    # ---------------------------
    # Pagination helpers
    # ---------------------------
    def paginate_pages(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        parser: TypingCallable[[Any], T] | None = None,
    ) -> Iterator[Page[T]]:
        page = self._get_page(path, params=params, parser=parser)
        yield page
        next_url = page.next
        while next_url:
            page = self._get_page(next_url, parser=parser)
            yield page
            next_url = page.next

    def paginate_items(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        parser: TypingCallable[[Any], T] | None = None,
    ) -> Iterator[T]:
        for page in self.paginate_pages(path, params=params, parser=parser):
            for item in page.results:
                yield item

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
