"""Models for user-related data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .institutions import Institution


class UserSlim(BaseModel):
    """Fields of UserRetrieveSlimSerializer."""

    id: int
    first_name: str
    last_name: str
    email: str
    affiliation: Institution
    is_authorized_investigator: bool = Field(default=False)
    orcid: str | None = None
    url: str | None = None
    has_avatar: bool = Field(default=False)

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class SuspendedBy(BaseModel):
    """Minimal representation of a suspending user for display."""

    id: int
    name: str


class UserPublic(UserSlim):
    """Fields of UserRetrievePublicSerializer."""

    # institution_sponsorships: filled via separate endpoints; keep optional list placeholder
    institution_sponsorships: list[dict[str, object]] | None = None
    current_affiliates: list[UserSlim] = Field(default_factory=list)
    current_sponsors: list[UserSlim] = Field(default_factory=list)
    is_suspended: bool = Field(default=False)
    suspended_by: SuspendedBy | None = None


class UserSelf(UserPublic):
    """Fields of UserRetrieveSelfSerializer."""

    pending_institution_requests: list[dict[str, object]] = Field(default_factory=list)
    pending_affiliate_requests: list[dict[str, object]] = Field(default_factory=list)
    phone: str | None = None
    totp_enrolled_at: datetime | None = None
    finished_registration: bool | None = None
    has_api_access: bool = Field(default=False)
