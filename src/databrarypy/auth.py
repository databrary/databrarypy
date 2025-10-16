from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass
class OAuth2Token:
    """OAuth2 token with expiration tracking.

    Attributes:
        access_token: The OAuth2 access token.
        refresh_token: Optional refresh token for obtaining new access tokens.
        expires_at: Token expiration time in epoch seconds.
    """

    access_token: str
    refresh_token: str | None
    expires_at: float

    @property
    def should_refresh(self) -> bool:
        """Return True if the token is expired or within the 30s refresh window."""
        return time.time() >= (self.expires_at - 30)


class OAuth2Client:
    """OAuth2 client for Databrary authentication.

    Handles password grant and refresh token flows using the `/o/token/` endpoint.
    Expects OAuth2-standard snake_case response fields.
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
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)
        self._token: OAuth2Token | None = None

    def _request_token(self, data: dict[str, str]) -> OAuth2Token:
        """Request an OAuth2 token from the server.

        Args:
            data: Form data for the token request.

        Returns:
            OAuth2Token containing access token, refresh token, and expiration.

        Raises:
            RuntimeError: If the token request fails.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = self._http.post("/o/token/", data=data, headers=headers)
        if resp.is_error:
            raise RuntimeError(f"Token request failed {resp.status_code}: {resp.text}")
        payload = resp.json()
        access_token = payload["access_token"]
        refresh_token = payload.get("refresh_token")
        expires_in = payload.get("expires_in", 3600)
        return OAuth2Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=time.time() + float(expires_in),
        )

    def login(self) -> OAuth2Token:
        """Authenticate using the credentials provided at initialization.

        Returns:
            OAuth2Token containing the access and refresh tokens.

        Raises:
            RuntimeError: If authentication fails.
        """
        self._token = self._request_token(
            {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )
        return self._token

    def refresh(self) -> OAuth2Token:
        """Refresh the access token using the refresh token.

        Returns:
            OAuth2Token with new access and refresh tokens.

        Raises:
            RuntimeError: If no refresh token is available or refresh fails.
        """
        if not self._token or not self._token.refresh_token:
            raise RuntimeError("No refresh token available.")
        self._token = self._request_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": self._token.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )
        return self._token

    def get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            A valid access token string.

        Raises:
            RuntimeError: If not authenticated or token cannot be refreshed.
        """
        if not self._token:
            raise RuntimeError("Not authenticated. Call login_with_password() first.")
        if self._token.should_refresh:
            if self._token.refresh_token:
                self.refresh()
            else:
                raise RuntimeError("Access token expired and no refresh token.")
        return self._token.access_token
