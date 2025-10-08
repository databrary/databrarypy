"""Pydantic models for permission and release level constants.

These mirror backend enums to make them available on the client side
without dedicated API endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PermissionLevels(BaseModel):
    """Client-side representation of permission/access levels.

    These align with backend enums:
    - VolumeAccessLevel
    - VolumeCollaboratorAccessLevel
    """

    volume_access_levels: list[str] = Field(
        default_factory=lambda: [
            "superuser",
            "owner",
            "investigator",
            "read write",
            "read only",
            "read only shared",
            "read only public",
            "read only overview",
            "none",
        ]
    )
    volume_collaborator_access_levels: list[str] = Field(
        default_factory=lambda: [
            "investigator",
            "read write",
            "read only",
            "none",
        ]
    )

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class ReleaseLevel(BaseModel):
    """Single release level with code and human-readable description."""

    code: str
    description: str


class ReleaseLevels(BaseModel):
    """Client-side representation of file sharing (release) levels.

    Mirrors backend FileSharingLevel enums.
    """

    levels: list[ReleaseLevel] = Field(
        default_factory=lambda: [
            ReleaseLevel(
                code="private",
                description=("This content is not shared and is restricted to collaborators."),
            ),
            ReleaseLevel(
                code="authorized_users",
                description=(
                    "This content is restricted to authorized Databrary users and may not be redistributed in any form."
                ),
            ),
            ReleaseLevel(
                code="learning_audiences",
                description=(
                    "This content is restricted to authorized Databrary users, who may use clips or images from it in presentations for informational or educational purposes. Such presentations may be videotaped or recorded and those videos or recordings may then be made available to the public via the internet (e.g., YouTube)."
                ),
            ),
            ReleaseLevel(
                code="public",
                description="This content is available to the public.",
            ),
        ]
    )

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
