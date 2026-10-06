# databrarypy – Databrary API Python Client

A typed Python client for the Databrary API, built on httpx and pydantic. It provides access to users, volumes, sessions, folders, records, search, and system metadata, with robust retry/backoff, pagination, and binary downloads.

- Python: 3.12+
- Repo: `https://github.com/databrary/databrarypy`

## Onboarding & requirements

- Request API access for your account from an admin.
- Create an OAuth2 client in your web profile to get `client_id` and `client_secret` (store the secret safely).
- The token endpoint (`/o/token/`) follows OAuth2 with a password grant and returns snake_case fields; application endpoints mostly return camelCase keys. This client normalizes response keys to snake_case by default (`snake_case=True`). Pydantic models in this package expect **snake_case** payloads—the same shape you get from the client under that default. If you set `snake_case=False`, normalize manually with `databrarypy.utils.case.snake_keys` before calling `model_validate` on those models.

## Installation

```bash
pip install databrarypy
# or from this repo
poetry install
```

## Quickstart

```python
from databrarypy import DatabraryClient

client = DatabraryClient(
    base_url="https://api.databrary.org",
    client_id="<client-id>",
    client_secret="<client-secret>",
    username="<username>",
    password="<password>",
)
client.auth.login()

print(client.whoami().model_dump())
print(client.system.get_db_stats().model_dump())
```

## Initialize from .env (from_env)

You can configure the client via a `.env` file using `DatabraryClient.from_env(...)`.

```python
from databrarypy import DatabraryClient

# Reads required settings from a .env file in the current directory.
# Set login=True to perform an OAuth2 login immediately.
client = DatabraryClient.from_env(login=True)

print(client.whoami().model_dump())
```

Required keys expected in the `.env` file:

```bash
BASE_URL=<base-url>
CLIENT_ID=<client-id>
CLIENT_SECRET=<client-secret>
USERNAME=<username>
PASSWORD=<password>
```

The User-Agent is set automatically to `databrarypy/<version>`.

If your `.env` file lives elsewhere, pass its path explicitly:

```python
from pathlib import Path
from databrarypy import DatabraryClient

env_path = Path(__file__).parent / ".env"
client = DatabraryClient.from_env(env_file=env_path, login=True)
```

## Usage highlights

- Pagination: `page(...)` returns a `Page[T]`, `list(...)` iterates all.
- Downloads: methods return bytes or stream to `dest_path`.

```python
for user in client.users.list(search="doe", page_size=100):
    print(user.id, user.full_name)

path = client.users.avatar(user_id=123, dest_path="/tmp/avatar.jpg")
```

## Authentication & token refresh

- Call `client.auth.login()` once after constructing the client. This performs an OAuth2 password grant at `/o/token/` and stores the returned `access_token`, optional `refresh_token`, and expiration time.
- Every API call obtains headers via the client, which calls `get_valid_access_token()` under the hood. If the token is close to expiry (within ~30 seconds) or expired, the client automatically attempts a refresh using the stored `refresh_token`.
- If no `refresh_token` is available or refresh fails, subsequent calls will raise an error and you should re-run `client.auth.login()`.

### Long-running scripts (hours/days)

- Use a single `DatabraryClient` instance for the lifetime of your process and call `client.auth.login()` once at startup.
- The client will transparently refresh the access token during requests when needed. You do not need to schedule periodic refreshes yourself.


## Example script

The `example/example.py` script demonstrates records management (create, update,
delete records and measures, assign records to files). It runs interactively,
prompting for a volume ID and then a menu of operations.

### Prepare .env

Create `example/.env` with your Databrary API credentials (this file is
gitignored and must not be committed):

```bash
BASE_URL=https://api.databrary.org
CLIENT_ID=<your-client-id>
CLIENT_SECRET=<your-client-secret>
USERNAME=<your-email>
PASSWORD=<your-password>
```

Obtain `CLIENT_ID` and `CLIENT_SECRET` from your Databrary web profile
(OAuth2 client). Request API access from an admin if needed.

### Build and run

```bash
# Install dependencies (if not already done)
poetry install

# Run the example
poetry run python example/example.py
```

## Development

```bash
make install
make test
make lint
make format
make type-check
make docs
make docs-serve
```

## API Reference

- Generated from docstrings with pdoc. Build locally with `make docs` and open `docs/index.html`, or serve with `make docs-serve`.
- Hosted docs (GitHub Pages): see the repository’s Pages site once the workflow runs on `main`.
