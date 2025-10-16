# databrarypy

Python client for the [Databrary](https://databrary.org) API with OAuth2 authentication.

## Installation

```bash
pip install databrarypy
```

## Quick Start

```python
from databrarypy import DatabraryClient

# Create client
client = DatabraryClient(
    base_url="https://nyu.databrary.org",
    client_id="your_client_id",
    client_secret="your_client_secret",
    username="user@example.com",
    password="password",
    user_agent="your_user_agent"
)

# Authenticate
client.auth.login()

# Get authenticated user info
user_info = client.whoami()
print(user_info)

# Get system statistics
stats = client.system.get_db_stats()
print(f"Institutions: {stats.institutions}")
print(f"Hours of recordings: {stats.hours_of_recordings}")

# List available asset formats
formats = client.system.list_asset_formats()
```

## API Overview

### Client

- `DatabraryClient(base_url, client_id, client_secret, username, password, user_agent)` - Main API client
- `client.whoami()` - Get authenticated user information

### Authentication

- `client.auth.login()` - Authenticate using credentials provided at initialization
- `client.auth.refresh()` - Manually refresh access token
- `client.auth.get_valid_access_token()` - Get valid token (auto-refreshes if expired)

### System Resources

- `client.system.get_db_stats()` - Get Databrary statistics
- `client.system.list_asset_formats()` - Get available asset formats

## Development

```bash
# Install dependencies
poetry install

# Run tests
make test

# Format and lint
make format
make lint

# All checks (format, lint, type-check, test)
make all
```

This project uses [Conventional Commits](https://www.conventionalcommits.org/) - use `cz commit` instead of `git commit`.

## Requirements

- Python 3.12+
- httpx >= 0.27
- pydantic >= 2.7
