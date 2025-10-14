"""Volume list/detail and collaborator/owner related models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .files import File
from .institution_sponsorship import InstitutionSponsorship
from .institutions import Institution
from .sponsorships import Sponsorship
from .users import UserSlim
from .volume_coauthors import VolumeCoauthor
from .volume_shared import Category, Citation, FileCounts, Metric, VolumeFundingRead, VolumeLink


class VolumePreview(BaseModel):
    """PreviewVolumeSerializer fields."""

    id: int
    updated_at: object | None = None
    created_at: object | None = None
    title: str
    description: str | None = None
    short_name: str | None = None
    sharing_level: str
    coauthors: list[VolumeCoauthor] = Field(default_factory=list)
    owner_connection: InstitutionSponsorship | None = None
    owner_institution: Institution | None = None
    access_level: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class VolumeListItem(BaseModel):
    """Volume list item (VolumeListSerializer)."""

    id: int
    title: str
    short_name: str | None = None
    sharing_level: str
    owner_connection: InstitutionSponsorship | None = None
    owner_institution: Institution | None = None
    access_level: str | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class VolumeDetail(VolumePreview):
    """Full VolumeSerializer subset used by client."""

    owner_connection: InstitutionSponsorship | None = None
    owner_institution: Institution | None = None
    sharing_level: str
    fundings: list[VolumeFundingRead] = Field(default_factory=list)
    links: list[VolumeLink] = Field(default_factory=list)
    enabled_categories: list[Category] = Field(default_factory=list)
    enabled_metrics: list[Metric] = Field(default_factory=list)
    access_level: str | None = None
    has_admin_access: bool | None = None
    citation: Citation | str | None = None
    session_count: int | None = None
    session_count_shared: int | None = None
    participant_count: int | None = None
    participant_gender_counts: dict[str, int] | None = None
    file_counts: FileCounts | None = None
    thumbnail: File | None = None

    model_config = {"populate_by_name": True, "extra": "forbid"}


class VolumeCollaborator(BaseModel):
    """Collaborator row."""

    id: int
    volume: int
    user: UserSlim
    sponsor: UserSlim | None = None
    sponsorship: Sponsorship | None = None
    is_publicly_visible: bool
    access_level: str
    expiration_date: object | None = None
    sponsored_users: list[UserSlim] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "forbid"}
