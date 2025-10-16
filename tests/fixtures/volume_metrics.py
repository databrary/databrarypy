"""Volume metrics and categories fixtures."""

from __future__ import annotations

# ---- Metrics and Categories ----
MOCK_VOLUME_METRICS = [
    {
        "id": 1,
        "name": "ID",
        "release": "PUBLIC",
        "type": "text",
        "options": None,
        "assumed": None,
        "description": "A unique, anonymized, primary identifier, such as participant ID",
        "required": True,
    }
]

MOCK_VOLUME_CATEGORIES = [
    {
        "id": 7,
        "name": "context",
        "description": "A particular setting or other aspect of where/when/how data were collected",
        "metrics": [
            {
                "id": 32,
                "name": "name",
                "release": "PUBLIC",
                "type": "text",
                "options": None,
                "assumed": None,
                "description": "A label or identifier for the context",
                "required": False,
            }
        ],
    }
]

MOCK_VOLUME_CITATION = {
    "authors": "Smith, J., Johnson, J. & Doe, A.",
    "year": 2025,
    "title": "Sample Research Dataset Collection",
    "institution": "Example University",
    "retrieval_date": "October 10, 2025",
    "volume_id": 1,
}
