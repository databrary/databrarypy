"""Pydantic models for read-only search results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserSearchResult(BaseModel):
    """Single user result returned by the search endpoint."""

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


class InstitutionSearchResult(BaseModel):
    """Institution search result from the search endpoint."""

    id: int
    name: str
    url: str | None = None
    has_avatar: bool
    score: float | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class VolumeOwner(BaseModel):
    """Nested owner object in the search endpoint."""

    user_id: int | None = None
    full_name: str | None = None
    institution_name: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class VolumeSearchResult(BaseModel):
    """Volume search result from the search endpoint."""

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
