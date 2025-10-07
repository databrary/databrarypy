"""Models for asset format data."""

from __future__ import annotations

from pydantic import BaseModel, Field, RootModel


class Format(BaseModel):
    """Asset format information.

    Attributes:
        id: Format ID.
        mimetype: MIME type string.
        name: Human-readable format name.
        extensions: List of file extensions for this format.
    """

    id: int
    mimetype: str
    name: str
    extensions: list[str] = Field(default_factory=list)


class GroupedFormats(RootModel[dict[str, list[Format]]]):
    """Formats grouped by category (e.g., Video, Audio)."""
