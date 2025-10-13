"""Pydantic models for read-only search results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserSearchHit(BaseModel):
    """User search hit shape from UserSearchSerializer.

    Field names are snake_case to align with client-side normalization.
    """

    id: int
    first_name: str
    last_name: str
    full_name: str
    email: str
    orcid: str | None = None
    url: str | None = None
    is_authorized: bool
    has_avatar: bool
    score: float | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class InstitutionSearchHit(BaseModel):
    """Institution search hit from InstitutionSearchSerializer."""

    id: int
    name: str
    url: str | None = None
    has_avatar: bool
    score: float | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class VolumeOwner(BaseModel):
    """Nested owner object in VolumeSearchSerializer."""

    user_id: int | None = None
    full_name: str | None = None
    institution_name: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class VolumeSearchHit(BaseModel):
    """Volume search hit from VolumeSearchSerializer."""

    id: int
    title: str
    description: str
    owner: VolumeOwner
    tags: list[str] = Field(default_factory=list)
    file_types: list[str] = Field(default_factory=list)
    has_session: bool
    sharing_level: str | None = None
    score: float | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
