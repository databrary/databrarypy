"""Tags resource for read-only endpoints."""

from __future__ import annotations

from typing import Iterator

from ..models import Page, Tag
from ._base import BaseResource


class TagsResource(BaseResource):
    """List and retrieve tags."""

    def page(
        self,
        *,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
    ) -> Page[Tag]:
        """List tags with optional search query."""
        params = self.build_params(search=search, page=page, page_size=page_size, ordering=ordering)
        return self._get_page("/tags/", params=params, parser=Tag.model_validate)

    def list(
        self,
        *,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
    ) -> Iterator[Tag]:
        """Iterate tags across pages yielding `Tag` objects."""
        params = self.build_params(search=search, page=page, page_size=page_size, ordering=ordering)
        return self.paginate_items("/tags/", params=params, parser=Tag.model_validate)

    def retrieve(self, tag_id: int) -> Tag:
        """Retrieve a single tag by id."""
        data = self._get_json(f"/tags/{tag_id}/")
        return Tag.model_validate(data)
