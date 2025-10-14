"""Categories resource for read-only endpoints."""

from __future__ import annotations

from ..models import Category
from ._base import BaseResource


class CategoriesResource(BaseResource):
    """List and retrieve categories (with nested metrics)."""

    def list(
        self,
    ) -> list[Category]:
        """List categories."""
        data = self._get_json("/categories/")
        items = data if isinstance(data, list) else data.get("results", [])
        return [Category.model_validate(item) for item in items]

    def retrieve(self, category_id: int) -> Category:
        """Retrieve a single category by id (includes nested metrics)."""
        data = self._get_json(f"/categories/{category_id}/")
        return Category.model_validate(data)
