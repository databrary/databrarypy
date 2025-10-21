"""Models for sponsorship-related data."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from .institutions import Institution
from .users import UserSlim


class Sponsorship(BaseModel):
    """Sponsorship serializer fields (SponsorshipSerializer)."""

    id: int
    sponsor: UserSlim
    user: UserSlim
    institution: Institution
    access_level: str
    has_databrary_affiliate_access: bool
    request: int | None = None
    sponsor_institution_connection: int
    expiration_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
