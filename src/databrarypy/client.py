from __future__ import annotations

import os
from collections.abc import Callable
from contextlib import suppress
from types import TracebackType
from typing import Any

import httpx
from dotenv import dotenv_values

from .auth import OAuth2Client
from .models import WhoAmI
from .resources import (
    CategoriesResource,
    FoldersResource,
    FundersResource,
    InstitutionsResource,
    RecordsResource,
    SearchResource,
    SessionsResource,
    SystemResource,
    TagsResource,
    UsersResource,
)
from .resources.volumes import VolumesResource
from .utils.case import snake_keys


class DatabraryClient:
    """Databrary API client using OAuth2 authentication.

    This client handles authentication and provides access to Databrary API resources.
    All requests include required headers including User-Agent.

    Attributes:
        auth: OAuth2Client for authentication management.
        system: SystemResource for system-wide operations.
    """

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        user_agent: str,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        snake_case: bool = True,
        max_retries: int = 5,
        respect_retry_after: bool = True,
        backoff_base: float = 0.5,
        backoff_jitter: float = 0.25,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.auth = OAuth2Client(
            base_url=self.base_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent,
            timeout=timeout,
            transport=transport,
        )
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)
        self._closed = False

        self._normalize: Callable[[Any], Any] = (
            (lambda d: snake_keys(d)) if snake_case else (lambda d: d)
        )
        self.system = SystemResource(self._http, self._headers, self._normalize)
        self.search = SearchResource(self._http, self._headers, self._normalize)
        self.users = UsersResource(self._http, self._headers, self._normalize)
        self.institutions = InstitutionsResource(self._http, self._headers, self._normalize)
        self.volumes = VolumesResource(self._http, self._headers, self._normalize)
        self.sessions = SessionsResource(self._http, self._headers, self._normalize)
        self.folders = FoldersResource(self._http, self._headers, self._normalize)
        self.records = RecordsResource(self._http, self._headers, self._normalize)
        self.funders = FundersResource(self._http, self._headers, self._normalize)
        self.tags = TagsResource(self._http, self._headers, self._normalize)
        self.categories = CategoriesResource(self._http, self._headers, self._normalize)

        # Apply retry configuration to all resources (attributes exist on BaseResource)
        for res in (
            self.system,
            self.search,
            self.users,
            self.institutions,
            self.volumes,
            self.sessions,
            self.folders,
            self.records,
            self.funders,
            self.tags,
            self.categories,
        ):
            res._max_retries = max(0, int(max_retries))
            res._respect_retry_after = bool(respect_retry_after)
            res._backoff_base = float(backoff_base)
            res._backoff_jitter = float(backoff_jitter)

    def _ensure_open(self) -> None:
        """Raise if the client has already been closed."""
        if self._closed:
            raise RuntimeError("DatabraryClient is closed.")

    def _headers(self) -> dict[str, str]:
        """Generate headers for API requests with valid authentication.

        Returns:
            Dictionary of HTTP headers including authorization token.
        """
        self._ensure_open()
        token = self.auth.get_valid_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    def whoami(self) -> WhoAmI:
        """Get information about the authenticated user.

        Returns:
            Dictionary containing user information and authentication method.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        self._ensure_open()
        resp = self._http.get("/oauth2/test/", headers=self._headers())
        resp.raise_for_status()
        raw = resp.json()
        return WhoAmI.model_validate(raw)

    def close(self) -> None:
        """Close the underlying HTTP clients."""
        if self._closed:
            return
        self.auth.close()
        self._http.close()
        self._closed = True

    def __enter__(self) -> "DatabraryClient":
        """Enter the context manager, returning ``self``."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the HTTP clients."""
        self.close()

    def __del__(self) -> None:  # pragma: no cover - best-effort cleanup
        """Ensure resources are freed when the client is garbage collected."""
        with suppress(Exception):
            self.close()

    @classmethod
    def from_env(
        cls,
        *,
        env_file: str | os.PathLike[str] | None = None,
        login: bool = False,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        snake_case: bool = True,
        max_retries: int = 5,
        respect_retry_after: bool = True,
        backoff_base: float = 0.5,
        backoff_jitter: float = 0.25,
    ) -> "DatabraryClient":
        """Instantiate a client using configuration sourced from environment variables.

        Args:
            env_file: Optional path to a ``.env`` file. Environment variables take precedence
                over values loaded from the file.
            login: Whether to perform an immediate OAuth2 login.
            timeout: HTTP client timeout in seconds.
            transport: Optional custom transport for httpx (primarily for testing).
            snake_case: Whether API responses should be normalized to ``snake_case``.
            max_retries: Maximum number of retries for transient errors.
            respect_retry_after: Honor ``Retry-After`` headers when retrying.
            backoff_base: Base value for exponential backoff between retries.
            backoff_jitter: Random jitter applied to retry delays.

        Returns:
            Configured ``DatabraryClient`` instance.

        Raises:
            RuntimeError: If required configuration values are missing.
        """
        env_values: dict[str, str] = (
            dotenv_values() if env_file is None else dotenv_values(str(env_file))
        )

        required_settings: dict[str, str] = {
            "base_url": "BASE_URL",
            "client_id": "CLIENT_ID",
            "client_secret": "CLIENT_SECRET",
            "username": "USERNAME",
            "password": "PASSWORD",
            "user_agent": "USER_AGENT",
        }
        resolved = {name: env_values.get(key) for name, key in required_settings.items()}
        missing = [name for name, value in resolved.items() if value is None]
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise RuntimeError(f"Missing required configuration values: {missing_list}")

        resolved_str = {name: value for name, value in resolved.items() if value is not None}

        client = cls(
            base_url=resolved_str["base_url"],
            client_id=resolved_str["client_id"],
            client_secret=resolved_str["client_secret"],
            username=resolved_str["username"],
            password=resolved_str["password"],
            user_agent=resolved_str["user_agent"],
            timeout=timeout,
            transport=transport,
            snake_case=snake_case,
            max_retries=max_retries,
            respect_retry_after=respect_retry_after,
            backoff_base=backoff_base,
            backoff_jitter=backoff_jitter,
        )

        if login:
            client.auth.login()
        return client
