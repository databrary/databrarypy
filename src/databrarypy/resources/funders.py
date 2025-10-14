"""Funders resource for read-only endpoints."""

from __future__ import annotations

from ..models import Funder
from ._base import BaseResource


class FundersResource(BaseResource):
    """List and retrieve funders."""

    def list(
        self,
        *,
        include_all: bool | None = None,
        is_approved: bool | None = None,
    ) -> list[Funder]:
        """List funders.

        include_all translates to query param `all=true` (backend shows unapproved only to privileged users).
        """
        params = self.build_params(is_approved=is_approved)
        if include_all:
            params["all"] = "true"
        data = self._get_json("/funders/", params=params)
        items = data if isinstance(data, list) else data.get("results", [])
        return [Funder.model_validate(item) for item in items]

    def retrieve(self, funder_id: int) -> Funder:
        """Retrieve a single funder by id."""
        data = self._get_json(f"/funders/{funder_id}/")
        return Funder.model_validate(data)
