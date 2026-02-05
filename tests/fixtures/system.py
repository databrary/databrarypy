"""System resource test fixtures."""

import httpx

from .auth import handle_token_success
from .common import build_transport

# Mock system response data
MOCK_SYSTEM_RESPONSES = {
    "stats": {
        "institutions": 5,
        "affiliates": 10,
        "investigators": 20,
        "hours_of_recordings": 42,
    },
    "formats": {
        "Video": [
            {
                "id": 1,
                "mimetype": "video/mp4",
                "name": "MPEG-4 video",
                "extensions": ["mp4", "m4v"],
            },
            {
                "id": 2,
                "mimetype": "video/webm",
                "name": "WebM video",
                "extensions": ["webm"],
            },
        ],
        "Audio": [
            {
                "id": 3,
                "mimetype": "audio/mpeg",
                "name": "MP3 audio",
                "extensions": ["mp3"],
            },
            {
                "id": 4,
                "mimetype": "audio/wav",
                "name": "WAV audio",
                "extensions": ["wav"],
            },
        ],
        "Image": [
            {
                "id": 5,
                "mimetype": "image/jpeg",
                "name": "JPEG image",
                "extensions": ["jpg", "jpeg"],
            }
        ],
    },
}


# Handler functions for system endpoints
def handle_stats(request: httpx.Request) -> httpx.Response:
    """Handle statistics endpoint."""
    return httpx.Response(200, json=MOCK_SYSTEM_RESPONSES["stats"])


def handle_formats(request: httpx.Request) -> httpx.Response:
    """Handle asset formats endpoint."""
    return httpx.Response(200, json=MOCK_SYSTEM_RESPONSES["formats"])


# Transport builder for system resource tests
def build_system_transport(
    token_handler=handle_token_success,
    stats_handler=handle_stats,
    formats_handler=handle_formats,
):
    """Build transport for system resource tests.

    Args:
        token_handler: Handler for authentication.
        stats_handler: Handler for stats endpoint.
        formats_handler: Handler for formats endpoint.
    """
    return build_transport(
        ("POST", "/o/token/", token_handler),
        ("GET", "/statistics/summary/", stats_handler),
        ("GET", "/grouped-formats/", formats_handler),
    )
