"""Typed exceptions for Databrary API client."""

from __future__ import annotations

from dataclasses import dataclass


class ApiError(Exception):
    """Base class for API-related errors."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class UnauthorizedError(ApiError):
    """401 Unauthorized."""


class ForbiddenError(ApiError):
    """403 Forbidden."""


class NotFoundError(ApiError):
    """404 Not Found."""


@dataclass
class RateLimitError(ApiError):
    """429 Too Many Requests.

    retry_after: optional number of seconds suggested by the server.
    """

    retry_after: float | None = None

    def __init__(
        self, message: str, *, status_code: int | None = 429, retry_after: float | None = None
    ) -> None:  # noqa: D401 - message docs inherited
        super().__init__(message, status_code=status_code)
        self.retry_after = retry_after


class ServerError(ApiError):
    """5xx Server error after retries exhausted."""
