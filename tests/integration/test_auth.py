from __future__ import annotations

from databrarypy.client import DatabraryClient


def test_whoami(client: DatabraryClient):
    data = client.whoami()
    # Validate expected fields exist on the model
    assert hasattr(data, "user")
    assert hasattr(data, "auth_method")
