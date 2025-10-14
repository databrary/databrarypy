import os
from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient

pytestmark = pytest.mark.staging


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    try:
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and os.environ.get(key) is None:
                os.environ[key] = val
    except Exception:
        # Best-effort loader; ignore malformed lines
        pass


@pytest.fixture(scope="session")
def client() -> DatabraryClient:
    # Load credentials from example/.env if present
    env_path = Path(__file__).resolve().parents[2] / "example" / ".env"
    _load_env_file(env_path)

    base_url = os.environ.get("BASE_URL")
    user_agent = os.environ.get("USER_AGENT")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if not all([base_url, user_agent, client_id, client_secret, username, password]):
        raise RuntimeError(
            "Missing required env vars (BASE_URL, USER_AGENT, CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD)"
        )

    c = DatabraryClient(
        base_url=base_url, client_id=client_id, client_secret=client_secret, user_agent=user_agent
    )
    c.auth.login_with_password(username, password)
    return c
