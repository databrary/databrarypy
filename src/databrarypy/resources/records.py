"""Records resource for Databrary API (read-only)."""

from __future__ import annotations

from typing import Iterator

from ..models import Page
from ..models.records import Record
from ._base import BaseResource


class RecordsResource(BaseResource):
    """List and retrieve records (measures included)."""

    def page(
        self,
        volume_id: int,
        *,
        category_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[Record]:
        """List records in a volume (paginated)."""
        params = self.build_params(
            category_id=category_id,
            page=page,
            page_size=page_size,
        )
        return self._get_page(
            f"/volumes/{volume_id}/records/",
            params=params,
            parser=Record.model_validate,
        )

    def list(
        self,
        volume_id: int,
        *,
        category_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Iterator[Record]:
        """Iterate records in a volume across pages yielding `Record` objects."""
        params = self.build_params(
            category_id=category_id,
            page=page,
            page_size=page_size,
        )
        return self.paginate_items(
            f"/volumes/{volume_id}/records/",
            params=params,
            parser=Record.model_validate,
        )

    def retrieve(self, volume_id: int, record_id: int) -> Record:
        """Retrieve a single record by id within a volume."""
        data = self._get_json(f"/volumes/{volume_id}/records/{record_id}/")
        return Record.model_validate(data)
