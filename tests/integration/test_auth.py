from __future__ import annotations

from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient


def test_whoami(client: DatabraryClient):
    data = client.whoami()
    # Validate expected fields exist on the model
    assert hasattr(data, "user")
    assert hasattr(data, "auth_method")


def test_client_context_manager_loads_env():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        pytest.skip(".env not available for integration test")

    with DatabraryClient.from_env(env_file=env_path, login=True) as ctx_client:
        assert ctx_client.auth._token is not None

    assert ctx_client._closed is True
