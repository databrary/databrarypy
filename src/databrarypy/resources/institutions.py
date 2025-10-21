"""Institutions resource for Databrary API."""

from __future__ import annotations

import builtins

from ..models import Institution, Page, UserSlim
from ._base import BaseResource


class InstitutionsResource(BaseResource):
    """Resource for institution endpoints."""

    def list(
        self,
        *,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[Institution]:
        """List institutions with optional search and pagination."""
        params = self.build_params(search=search, page=page, page_size=page_size)
        return self._get_page(
            "/institutions/",
            params=params,
            parser=Institution.model_validate,
        )

    def retrieve(self, institution_id: int) -> Institution:
        """Retrieve a single institution by ID."""
        data = self._get_json(f"/institutions/{institution_id}/")
        return Institution.model_validate(data)

    def avatar(self, institution_id: int, *, dest_path: str | None = None) -> bytes | str:
        """Download an institution's avatar; return bytes or save to disk.

        If dest_path is provided, stream to file and return the full path; otherwise returns bytes.
        """
        url = f"/institutions/{institution_id}/avatar/"
        if dest_path is None:
            return self._download_bytes(url)
        return self._download_to_path(url, dest_path)

    def authorized_investigators(
        self, institution_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> builtins.list[UserSlim]:
        """Return current investigators (role == 'investigator') for an institution.

        This derives from the affiliates endpoint and filters by role client-side.
        """
        params = self.build_params(page=page, page_size=page_size)
        data = self._get_json(f"/institutions/{institution_id}/affiliates/", params=params)
        page_data = Page[dict[str, object]].model_validate(data)
        investigators: list[UserSlim] = []
        for item in page_data.results:
            # each item is a sponsorship with 'user' and 'role'
            if isinstance(item, dict) and item.get("role") == "investigator":
                user_data = item.get("user")
                if user_data is not None:
                    investigators.append(UserSlim.model_validate(user_data))
        return investigators
