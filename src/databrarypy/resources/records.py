"""Records resource for Databrary API."""

from __future__ import annotations

from typing import Any, Iterator

from ..models import Page
from ..models.records import Record
from ._base import BaseResource

_PRIORITY_METRIC_NAMES = ("name", "id", "description")


class RecordsResource(BaseResource):
    """CRUD operations for volume records, measures, and file assignments."""

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def _get_priority_metric_id(self, volume_id: int, category_id: int) -> int | None:
        """Resolve the name/ID metric for a category in a volume.

        Mirrors the R package's ``get_volume_record_name_metric_id`` /
        the frontend's ``getPriorityMetric`` logic:
        1. required metrics first
        2. then by name priority: name > id > description
        3. fallback: first available metric
        """
        vol_data = self._get_json(f"/volumes/{volume_id}/")
        if not isinstance(vol_data, dict):
            return None

        enabled_categories = vol_data.get("enabled_categories") or []
        enabled_metrics = vol_data.get("enabled_metrics") or []
        if not enabled_categories or not enabled_metrics:
            return None

        category = None
        for cat in enabled_categories:
            if int(cat.get("id", -1)) == category_id:
                category = cat
                break
        if category is None:
            return None

        cat_metrics = category.get("metrics") or []
        if not cat_metrics:
            return None

        enabled_metric_ids = {int(m["id"]) for m in enabled_metrics if "id" in m}
        available = [m for m in cat_metrics if int(m.get("id", -1)) in enabled_metric_ids]
        if not available:
            return None

        for m in available:
            if m.get("required"):
                return int(m["id"])
        for pname in _PRIORITY_METRIC_NAMES:
            for m in available:
                if (m.get("name") or "").lower() == pname:
                    return int(m["id"])

        return int(available[0]["id"])

    def create(
        self,
        volume_id: int,
        *,
        category_id: int,
        name: str,
        measures: dict[str, Any] | None = None,
        participant: dict[str, Any] | None = None,
    ) -> Record:
        """Create a new record in a volume.

        The *name* is resolved to the category's priority metric automatically.
        Additional metric values can be supplied via *measures*
        (mapping metric ID strings to values).

        For participant records, *participant* may contain a ``birthday``
        dict (year/month/day) or an ``age`` dict (years/months/days).
        """
        metric_id = self._get_priority_metric_id(volume_id, category_id)
        if metric_id is None:
            raise ValueError(
                f"Cannot resolve name metric for category {category_id} in volume {volume_id}"
            )

        merged_measures = dict(measures) if measures else {}
        merged_measures[str(metric_id)] = name

        body: dict[str, Any] = {
            "category_id": category_id,
            "measures": merged_measures,
        }
        if participant is not None:
            body["participant"] = participant

        data = self._post_json(f"/volumes/{volume_id}/records/", json=body)
        return Record.model_validate(data)

    def update(
        self,
        volume_id: int,
        record_id: int,
        *,
        measures: dict[str, Any] | None = None,
        participant: dict[str, Any] | None = None,
    ) -> Record:
        """Partial-update (PATCH) an existing record.

        Only the provided fields are modified.  Use this method when you
        need to set multiple measures at once or update participant-specific
        data (birthday / age).

        .. tip::

           To set a single measure, :meth:`set_measure` provides a simpler
           interface that creates or replaces the value in one call without
           requiring the full measures dict.
        """
        body: dict[str, Any] = {}
        if measures is not None:
            body["measures"] = measures
        if participant is not None:
            body["participant"] = participant
        if not body:
            raise ValueError("At least one of measures or participant must be provided")

        data = self._patch_json(f"/volumes/{volume_id}/records/{record_id}/", json=body)
        return Record.model_validate(data)

    def delete(self, volume_id: int, record_id: int) -> bool:
        """Soft-delete a record from a volume."""
        return self._delete_request(f"/volumes/{volume_id}/records/{record_id}/")

    # ------------------------------------------------------------------
    # Measures
    # ------------------------------------------------------------------

    def set_measure(
        self,
        volume_id: int,
        record_id: int,
        metric_id: int,
        *,
        value: str | int | float | dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update a single measure on a record (upsert).

        This is the simplest way to set an individual metric value.  The
        measure is created if it doesn't exist or replaced if it does.

        *value* may be a string, number, or a date dict
        (year/month/day/is_estimated).

        .. tip::

           To update multiple measures or participant data (birthday / age)
           in a single request, use :meth:`update` instead.
        """
        body: Any = value if isinstance(value, dict) else {"value": value}

        data = self._post_json(
            f"/volumes/{volume_id}/records/{record_id}/measures/{metric_id}/",
            json=body,
        )
        return data  # type: ignore[no-any-return]

    def delete_measure(self, volume_id: int, record_id: int, metric_id: int) -> bool:
        """Delete a measure from a record. Fails for required metrics."""
        return self._delete_request(
            f"/volumes/{volume_id}/records/{record_id}/measures/{metric_id}/"
        )
