"""Categories resource for read-only endpoints."""

from __future__ import annotations

from ..models import Category, Page
from ._base import BaseResource


class CategoriesResource(BaseResource):
    """List and retrieve categories (with nested metrics)."""

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
    ) -> Page[Category]:
        """List categories with optional pagination and ordering."""
        params = self.build_params(page=page, page_size=page_size, ordering=ordering)
        return self._get_page("/categories/", params=params, parser=Category.model_validate)

    def retrieve(self, category_id: int) -> Category:
        """Retrieve a single category by id (includes nested metrics)."""
        data = self._get_json(f"/categories/{category_id}/")
        return Category.model_validate(data)
