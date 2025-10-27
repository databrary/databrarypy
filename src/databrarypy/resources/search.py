"""Search resource providing read-only search endpoints."""

from __future__ import annotations

from typing import Any, Iterator

from ..models import Page
from ..models.search import (
    InstitutionSearchResult,
    UserSearchResult,
    VolumeSearchResult,
)
from ._base import BaseResource


class SearchResource(BaseResource):
    """Read-only search endpoints for users, institutions, and volumes."""

    def users_page(
        self,
        q: str | None = None,
        *,
        filter: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Page[UserSearchResult]:
        """Search users.

        Mirrors backend `/search/users/`, passing query and pagination params.
        """
        params = self.build_params(
            q=q,
            filter=filter,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return self._get_page(
            "/search/users/",
            params=params,
            parser=UserSearchResult.model_validate,
        )

    def users_list(
        self,
        q: str | None = None,
        *,
        filter: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Iterator[UserSearchResult]:
        """Iterate user search results across pages yielding `UserSearchResult`."""
        params = self.build_params(
            q=q,
            filter=filter,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return self.paginate_items(
            "/search/users/",
            params=params,
            parser=UserSearchResult.model_validate,
        )

    def institutions_page(
        self,
        q: str | None = None,
        *,
        page: int | None = None,
        page_size: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Page[InstitutionSearchResult]:
        """Search institutions."""
        params = self.build_params(
            q=q,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return self._get_page(
            "/search/institutions/",
            params=params,
            parser=InstitutionSearchResult.model_validate,
        )

    def institutions_list(
        self,
        q: str | None = None,
        *,
        page: int | None = None,
        page_size: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Iterator[InstitutionSearchResult]:
        """Iterate institution search results across pages."""
        params = self.build_params(
            q=q,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return self.paginate_items(
            "/search/institutions/",
            params=params,
            parser=InstitutionSearchResult.model_validate,
        )

    def volumes_page(
        self,
        q: str | None = None,
        *,
        files_release_levels: list[str] | None = None,
        tag: str | None = None,
        sharing_level: str | None = None,
        format_categories: list[str] | None = None,
        formats: list[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Page[VolumeSearchResult]:
        """Search volumes with optional filters.

        Backend accepts both `files_release_levels[]` and `files_release_levels` repeated
        parameters; httpx will encode lists as repeated keys, which the backend handles.
        """
        params: dict[str, Any] = self.build_params(
            q=q,
            tag=tag,
            sharing_level=sharing_level,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        if files_release_levels:
            params["files_release_levels"] = files_release_levels
        if format_categories:
            params["format_categories"] = format_categories
        if formats:
            params["formats"] = formats

        return self._get_page(
            "/search/volumes/",
            params=params,
            parser=VolumeSearchResult.model_validate,
        )

    def volumes_list(
        self,
        q: str | None = None,
        *,
        files_release_levels: list[str] | None = None,
        tag: str | None = None,
        sharing_level: str | None = None,
        format_categories: list[str] | None = None,
        formats: list[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Iterator[VolumeSearchResult]:
        """Iterate volume search results across pages."""
        params: dict[str, Any] = self.build_params(
            q=q,
            tag=tag,
            sharing_level=sharing_level,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        if files_release_levels:
            params["files_release_levels"] = files_release_levels
        if format_categories:
            params["format_categories"] = format_categories
        if formats:
            params["formats"] = formats
        return self.paginate_items(
            "/search/volumes/",
            params=params,
            parser=VolumeSearchResult.model_validate,
        )
