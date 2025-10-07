"""Models for library-related data."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LibraryStats(BaseModel):
    """Statistics about the Databrary library.

    Attributes:
        institutions: Number of institutions.
        affiliates: Number of affiliates.
        investigators: Number of investigators.
        hours_of_recordings: Total hours of recordings.
    """

    institutions: int = Field(default=0)
    affiliates: int = Field(default=0)
    investigators: int = Field(default=0)
    hours_of_recordings: int = Field(default=0)

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
