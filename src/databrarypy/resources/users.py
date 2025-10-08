"""Users resource for Databrary API."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Dict, List  # noqa: UP035

import httpx

from ..models import Page, Sponsorship, UserPublic, UserSelf, UserSlim, VolumePreview


class UsersResource:
    """Resource for user operations and related endpoints."""

    def __init__(self, http: httpx.Client, headers_fn: Callable[[], dict[str, str]]) -> None:
        self._http = http
        self._headers = headers_fn

    def list(
        self,
        *,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        include_suspended: bool | None = None,
        exclude_self: bool | None = None,
        is_authorized_investigator: bool | None = None,
        has_api_access: bool | None = None,
    ) -> Page:
        """List users with search and filter params; returns paginated results."""
        params: dict[str, Any] = {}
        if search:
            params["search"] = search
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if include_suspended is not None:
            params["include_suspended"] = str(include_suspended).lower()
        if exclude_self is not None:
            params["exclude_self"] = str(exclude_self).lower()
        if is_authorized_investigator is not None:
            params["is_authorized_investigator"] = str(is_authorized_investigator).lower()
        if has_api_access is not None:
            params["has_api_access"] = str(has_api_access).lower()

        resp = self._http.get("/users/", params=params, headers=self._headers())
        resp.raise_for_status()
        data = resp.json()
        # coerce results to UserSlim
        data["results"] = [UserSlim.model_validate(item) for item in data.get("results", [])]
        return Page.model_validate(data)

    def retrieve(self, user_id: int, *, for_self: bool = False) -> UserPublic | UserSelf:
        """Retrieve user profile; set for_self=True to parse self-only fields."""
        resp = self._http.get(f"/users/{user_id}/", headers=self._headers())
        resp.raise_for_status()
        payload = resp.json()
        if for_self:
            return UserSelf.model_validate(payload)
        return UserPublic.model_validate(payload)

    def sponsorships(self, user_id: int) -> List[Sponsorship]:  # noqa: UP006,UP035
        """List sponsorships where the given user is sponsored (read-only)."""
        resp = self._http.get(f"/users/{user_id}/sponsorships/", headers=self._headers())
        resp.raise_for_status()
        return [Sponsorship.model_validate(item) for item in resp.json()]

    def institution_sponsorships(self, user_id: int) -> List[Dict[str, Any]]:  # noqa: UP006,UP035
        """List user's institution sponsorships (PICs); detailed if self/admin."""
        resp = self._http.get(f"/users/{user_id}/institution-sponsors/", headers=self._headers())
        resp.raise_for_status()
        data: List[Dict[str, Any]] = resp.json()  # noqa: UP006,UP035
        return data

    def affiliates(self, sponsor_id: int, *, include_expired: bool | None = None) -> Page:
        """List affiliates sponsored by the given user (paginated)."""
        params: dict[str, Any] = {}
        if include_expired is not None:
            params["include_expired"] = str(include_expired).lower()
        resp = self._http.get(
            f"/users/{sponsor_id}/affiliates/", params=params, headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        # results are Sponsorships
        data["results"] = [Sponsorship.model_validate(item) for item in data.get("results", [])]
        return Page.model_validate(data)

    def volumes(
        self, user_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> Page:
        """List volumes related to the user; respects viewer access; paginated."""
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        resp = self._http.get(f"/users/{user_id}/volumes/", params=params, headers=self._headers())
        resp.raise_for_status()
        data = resp.json()
        data["results"] = [VolumePreview.model_validate(item) for item in data.get("results", [])]
        return Page.model_validate(data)

    def avatar_bytes(self, user_id: int) -> bytes:
        """Download avatar bytes for a user (empty if missing)."""
        resp = self._http.get(f"/users/{user_id}/avatar/", headers=self._headers())
        if resp.status_code == 404:
            return b""
        resp.raise_for_status()
        # The backend returns a redirect to nginx; httpx follows redirects by default, so content is bytes
        return resp.content
