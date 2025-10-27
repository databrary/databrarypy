from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient

pytestmark = pytest.mark.staging


@pytest.fixture(scope="session")
def client() -> DatabraryClient:
    env_path = Path(__file__).resolve().parents[2] / ".env"

    client = DatabraryClient.from_env(env_file=env_path, login=True)
    return client
