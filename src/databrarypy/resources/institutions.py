"""Institutions resource for Databrary API."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, List  # noqa: UP035

import httpx

from ..models import Institution, Page, UserSlim


class InstitutionsResource:
    """Resource for institution endpoints."""

    def __init__(self, http: httpx.Client, headers_fn: Callable[[], dict[str, str]]) -> None:
        self._http = http
        self._headers = headers_fn

    def list(
        self,
        *,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page:
        """List institutions with optional search and pagination."""
        params: dict[str, Any] = {}
        if search:
            params["search"] = search
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        resp = self._http.get("/institutions/", params=params, headers=self._headers())
        resp.raise_for_status()
        data = resp.json()
        data["results"] = [Institution.model_validate(item) for item in data.get("results", [])]
        return Page.model_validate(data)

    def retrieve(self, institution_id: int) -> Institution:
        """Retrieve a single institution by ID."""
        resp = self._http.get(f"/institutions/{institution_id}/", headers=self._headers())
        resp.raise_for_status()
        return Institution.model_validate(resp.json())

    def affiliates(
        self, institution_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> Page:
        """List current affiliates (PICs) of an institution."""
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        resp = self._http.get(
            f"/institutions/{institution_id}/affiliates/", params=params, headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        # results are InstitutionSponsorshipSerializer objects; keep as dicts
        return Page.model_validate(data)

    def avatar_bytes(self, institution_id: int) -> bytes:
        """Download avatar bytes for an institution (empty if missing)."""
        resp = self._http.get(f"/institutions/{institution_id}/avatar/", headers=self._headers())
        if resp.status_code == 404:
            return b""
        resp.raise_for_status()
        return resp.content

    def authorized_investigators(
        self, institution_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> List[UserSlim]:  # noqa: UP006,UP035
        """Return current investigators (role == 'investigator') for an institution.

        This derives from the affiliates endpoint and filters by role client-side.
        """
        page_data = self.affiliates(institution_id, page=page, page_size=page_size)
        investigators: list[UserSlim] = []
        for item in page_data.results:
            # each item is a sponsorship (PersonInstitutionConnection serializer) with 'user' and 'role'
            if isinstance(item, dict) and item.get("role") == "investigator":
                investigators.append(UserSlim.model_validate(item.get("user")))
        return investigators
