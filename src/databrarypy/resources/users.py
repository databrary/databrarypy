"""Users resource for Databrary API."""

from __future__ import annotations

import builtins
from typing import Iterator

from ..models import (
    Page,
    Sponsorship,
    UserActivityItem,
    UserPublic,
    UserSelf,
    UserSlim,
    UserStatistics,
    VolumeListItem,
)
from ._base import BaseResource


class UsersResource(BaseResource):
    """Resource for user operations and related endpoints."""

    def page(
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
    ) -> Iterator[UserSlim]:
        """Iterate all users across pages yielding `UserSlim` objects."""
        params = self.build_params(
            search=search,
            page=page,
            page_size=page_size,
            include_suspended=include_suspended,
            exclude_self=exclude_self,
            is_authorized_investigator=is_authorized_investigator,
            has_api_access=has_api_access,
        )
        return self.paginate_items(
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

    def statistics(self, user_id: int) -> UserStatistics | None:
        """Retrieve statistics for a user.

        Returns ``None`` when the backend responds with 204 No Content
        (statistics have not been computed yet). Raises ``NotFoundError``
        when the user itself does not exist.
        """
        data = self._get_json_or_none(f"/users/{user_id}/statistics/")
        if data is None:
            return None
        return UserStatistics.model_validate(data)

    def sponsors(self, user_id: int) -> builtins.list[Sponsorship]:
        """Get active sponsorships where the given user is the affiliate.

        Returns Sponsorship objects including access level and expiration date.
        """
        data = self._get_json(f"/users/{user_id}/sponsorships/")
        return [Sponsorship.model_validate(item) for item in data]

    def affiliates(
        self,
        user_id: int,
        *,
        include_expired: bool | None = None,
    ) -> builtins.list[Sponsorship]:
        """Get sponsorships where the given user is the sponsor.

        Returns a list of Sponsorship objects or a list directly depending on backend;
        `include_expired=True` includes expired sponsorships.
        """
        params = self.build_params(include_expired=include_expired)
        data = self._get_json(f"/users/{user_id}/affiliates/", params=params)
        return [Sponsorship.model_validate(item) for item in data]

    def volumes_page(
        self, user_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> Page[VolumeListItem]:
        """List volumes related to the user; returns volume list items; paginated."""
        params = self.build_params(page=page, page_size=page_size)
        return self._get_page(
            f"/users/{user_id}/volumes/",
            params=params,
            parser=VolumeListItem.model_validate,
        )

    def volumes_list(
        self, user_id: int, *, page: int | None = None, page_size: int | None = None
    ) -> Iterator[VolumeListItem]:
        """Iterate all volumes for a user across pages yielding `VolumeListItem`."""
        params = self.build_params(page=page, page_size=page_size)
        return self.paginate_items(
            f"/users/{user_id}/volumes/",
            params=params,
            parser=VolumeListItem.model_validate,
        )

    def avatar(self, user_id: int, *, dest_path: str | None = None) -> bytes | str:
        """Download a user's avatar; return bytes or save to disk.

        If dest_path is provided, stream to file and return the full path; otherwise returns bytes.
        """
        url = f"/users/{user_id}/avatar/"
        if dest_path is None:
            # Keep empty-bytes behavior for missing avatars
            return self._download_bytes(url)
        # When saving, still succeed with 404? Be strict and raise for status; use streaming helper
        return self._download_to_path(url, dest_path)

    def activity_page(
        self,
        user_id: int,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[UserActivityItem]:
        """List user activity (profile changes, logins, sponsorships)."""
        params = self.build_params(page=page, page_size=page_size)
        return self._get_page(
            f"/users/{user_id}/history/",
            params=params,
            parser=UserActivityItem.model_validate,
        )

    def activity_list(
        self,
        user_id: int,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Iterator[UserActivityItem]:
        """Iterate user activity across pages yielding `UserActivityItem` objects."""
        params = self.build_params(page=page, page_size=page_size)
        return self.paginate_items(
            f"/users/{user_id}/history/",
            params=params,
            parser=UserActivityItem.model_validate,
        )
