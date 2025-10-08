from __future__ import annotations

from typing import Any

import httpx

from .auth import OAuth2Client
from .resources import InstitutionsResource, SystemResource, UsersResource


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
        self.system = SystemResource(self._http, self._headers)
        self.users = UsersResource(self._http, self._headers)
        self.institutions = InstitutionsResource(self._http, self._headers)

    def _headers(self) -> dict[str, str]:
        """Generate headers for API requests with valid authentication.

        Returns:
            Dictionary of HTTP headers including authorization token.
        """
        token = self.auth.get_valid_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    def whoami(self) -> dict[str, Any]:
        """Get information about the authenticated user.

        Returns:
            Dictionary containing user information and authentication method.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        resp = self._http.get("/oauth2/test/", headers=self._headers())
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        return data
