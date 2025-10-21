"""Users resource for Databrary API."""

from __future__ import annotations

import builtins

from ..models import Page, Sponsorship, UserPublic, UserSelf, UserSlim, VolumePreview
from ._base import BaseResource


class UsersResource(BaseResource):
    """Resource for user operations and related endpoints."""

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
    ) -> Page[UserSlim]:
        """List users with search and filter params; returns paginated results."""
        params = self.build_params(
            search=search,
            page=page,
            page_size=page_size,
            include_suspended=include_suspended,
            exclude_self=exclude_self,
            is_authorized_investigator=is_authorized_investigator,
            has_api_access=has_api_access,
        )
        return self._get_page(
            "/users/",
            params=params,
            parser=UserSlim.model_validate,
        )

    def retrieve(self, user_id: int, *, for_self: bool = False) -> UserPublic | UserSelf:
        """Retrieve user profile; set for_self=True to parse self-only fields."""
        payload = self._get_json(f"/users/{user_id}/")
        if for_self:
            return UserSelf.model_validate(payload)
        return UserPublic.model_validate(payload)

    def sponsors(self, user_id: int) -> builtins.list[Sponsorship]:
        """Get active sponsorships where the given user is the affiliate.

        Returns Sponsorship objects including access level and expiration date.
        """
        data = self._get_json(f"/users/{user_id}/sponsorships/")
        return [Sponsorship.model_validate(item) for item in data]

    def affiliates(
        self, user_id: int, *, include_expired: bool | None = None
    ) -> builtins.list[Sponsorship]:
        """Get sponsorships where the given user is the sponsor.

        Returns a list of Sponsorship objects; `include_expired=True` includes expired sponsorships.
        """
        params = self.build_params(include_expired=include_expired)
        data = self._get_json(
            f"/users/{user_id}/affiliates/",
            params=params,
        )
        return [Sponsorship.model_validate(item) for item in data]

    def volumes(
        self, user_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> Page[VolumePreview]:
        """List volumes related to the user; respects viewer access; paginated."""
        params = self.build_params(page=page, page_size=page_size)
        return self._get_page(
            f"/users/{user_id}/volumes/",
            params=params,
            parser=VolumePreview.model_validate,
        )

    def avatar_bytes(self, user_id: int) -> bytes:
        """Download avatar bytes for a user (empty if missing)."""
        # The backend returns a redirect to nginx; httpx follows redirects by default.
        return self._get_bytes_or_empty(f"/users/{user_id}/avatar/")
