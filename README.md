# databrarypy – Databrary API Python Client

A typed Python client for the Databrary API, built on httpx and pydantic. It provides access to users, volumes, sessions, folders, records, search, and system metadata, with robust retry/backoff, pagination, and binary downloads.

- Python: 3.12+
- Repo: `https://github.com/NYU-Databrary/databrarypy`

## Onboarding & requirements

- Request API access for your account from an admin.
- Obtain your secret User-Agent string from an admin
- Create an OAuth2 client in your web profile to get `client_id` and `client_secret` (store the secret safely).
- The token endpoint (`/o/token/`) follows OAuth2 with a password grant and returns snake_case fields; application endpoints mostly return camelCase keys. This client normalizes response keys to snake_case by default (`snake_case=True`).

## Installation

```bash
pip install databrarypy
# or from this repo
poetry install
```

## Quickstart

```python
from databrarypy import DatabraryClient

# user_agent must be your secret UA string provided by an admin
client = DatabraryClient(
    base_url="https://api.databrary.org",
    client_id="<client-id>",
    client_secret="<client-secret>",
    username="<username>",
    password="<password>",
    user_agent="<SECRET_USER_AGENT>",
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
USER_AGENT=<secret-user-agent>
```

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
