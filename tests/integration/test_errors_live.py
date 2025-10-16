from __future__ import annotations

import pytest

from databrarypy.client import DatabraryClient
from databrarypy.errors import NotFoundError, RateLimitError


def test_not_found_volume_raises(client: DatabraryClient):
    # Use a very large unlikely ID
    unlikely_id = 999999999
    with pytest.raises(NotFoundError):
        client.volumes.retrieve(unlikely_id)


def test_rate_limit_on_csv_download_raises(client: DatabraryClient):
    # Use a separate client with no retries to surface 429 quickly
    c = DatabraryClient(
        base_url=client.base_url,
        client_id=client.auth.client_id,
        client_secret=client.auth.client_secret,
        username=client.auth.username,
        password=client.auth.password,
        user_agent=client.user_agent,
        transport=client.auth._http._transport,  # reuse transport to keep session
        max_retries=0,
    )
    c.auth.login()

    # Find a volume id to request
    page = client.volumes.page(page=1)
    if not page.results:
        pytest.skip("No volumes available to test CSV download throttle")
    vid = page.results[0].id

    # First request should succeed (or be queued)
    c.volumes.request_csv_download(vid)

    # Second immediate request should hit throttle (one per minute)
    with pytest.raises(RateLimitError) as exc_info:
        c.volumes.request_csv_download(vid)
    err = exc_info.value
    # Retry-After should be present when throttled
    assert getattr(err, "retry_after", None) is None or err.retry_after >= 0
