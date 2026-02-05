from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .institutions import Institution

if TYPE_CHECKING:
    from .users import UserSlim


class InstitutionAccessRequest(BaseModel):
    """Access request for a user's role at a specific institution."""

    id: int
    user: "UserSlim"
    institution: Institution
    role: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
