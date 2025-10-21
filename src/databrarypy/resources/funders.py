"""Funders resource for read-only endpoints."""

from __future__ import annotations

from ..models import Funder, Page
from ._base import BaseResource


class FundersResource(BaseResource):
    """List and retrieve funders."""

    def list(
        self,
        *,
        include_all: bool | None = None,
        is_approved: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[Funder]:
        """List funders.

        include_all translates to query param `all=true` (backend shows unapproved only to privileged users).
        """
        params = self.build_params(
            is_approved=is_approved,
            page=page,
            page_size=page_size,
        )
        if include_all:
            params["all"] = "true"
        return self._get_page("/funders/", params=params, parser=Funder.model_validate)

    def retrieve(self, funder_id: int) -> Funder:
        """Retrieve a single funder by id."""
        data = self._get_json(f"/funders/{funder_id}/")
        return Funder.model_validate(data)
