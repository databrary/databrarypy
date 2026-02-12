"""Models for user-related data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .affiliate_requests import AffiliateAccessRequest
from .institution_requests import InstitutionAccessRequest
from .institution_sponsorship import InstitutionSponsorship
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
    # Some list responses include these public fields as well
    institution_sponsorships: list[InstitutionSponsorship] = Field(default_factory=list)
    current_affiliates: list["UserSlim"] = Field(default_factory=list)
    current_sponsors: list["UserSlim"] = Field(default_factory=list)
    is_suspended: bool = Field(default=False)
    suspended_by: SuspendedBy | None = None
    totp_enrolled_at: datetime | None = Field(
        default=None,
        description="Timestamp when user completed TOTP enrollment. Null means not enrolled.",
    )

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class SuspendedBy(BaseModel):
    """Minimal representation of a suspending user for display."""

    id: int
    name: str


class UserPublic(UserSlim):
    """Fields of UserRetrievePublicSerializer."""

    # institution_sponsorships: filled via separate endpoints; keep optional list placeholder
    institution_sponsorships: list[InstitutionSponsorship] = Field(default_factory=list)
    current_affiliates: list[UserSlim] = Field(default_factory=list)
    current_sponsors: list[UserSlim] = Field(default_factory=list)
    is_suspended: bool = Field(default=False)
    suspended_by: SuspendedBy | None = None
    # Some detail responses include self-only fields; accept as optional
    pending_institution_requests: list[InstitutionAccessRequest] = Field(default_factory=list)
    pending_affiliate_requests: list[AffiliateAccessRequest] = Field(default_factory=list)
    phone: str | None = None
    two_fa: str | None = None
    finished_registration: bool = Field(default=False)
    has_api_access: bool = Field(default=False)

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class UserSelf(UserPublic):
    """Fields of UserRetrieveSelfSerializer."""

    pending_institution_requests: list[InstitutionAccessRequest] = Field(default_factory=list)
    pending_affiliate_requests: list[AffiliateAccessRequest] = Field(default_factory=list)
    phone: str | None = None
    finished_registration: bool = Field(default=False)
    has_api_access: bool = Field(default=False)

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
