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
        transport=client.auth._http._transport,
        max_retries=0,
    )
    c.auth.login()

    page = client.volumes.page(page=1)
    if not page.results:
        pytest.skip("No volumes available to test CSV download throttle")
    vid = page.results[0].id

    # Fire two requests back-to-back; at least one must be rate-limited
    # (the throttle window may already be active from earlier tests).
    rate_limited = False
    for _ in range(2):
        try:
            c.volumes.request_csv_download(vid)
        except RateLimitError as err:
            rate_limited = True
            assert err.retry_after is None or err.retry_after >= 0
            break

    assert rate_limited, "Expected at least one RateLimitError from two rapid CSV download requests"
