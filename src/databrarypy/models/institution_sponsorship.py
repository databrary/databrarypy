"""Models for institution sponsorship/connection objects.

Matches the InstitutionSponsorshipSerializer shape on the backend.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .institutions import Institution

if TYPE_CHECKING:
    from .users import UserSlim


class InstitutionSponsorship(BaseModel):
    """PersonInstitutionConnection public shape with nested user/institution."""

    id: int
    institution: Institution
    user: "UserSlim"
    role: str
    expiration_date: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    request: int | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
