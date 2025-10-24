from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .users import UserSlim


class AffiliateAccessRequest(BaseModel):
    """Access request for affiliate sponsorship between users and institutions."""

    id: int
    requester: "UserSlim"
    sponsor: "UserSlim"
    access_level: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
