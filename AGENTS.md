# databrarypy – Agent Guide

This is a **typed Python client library** for the Databrary API (`https://api.databrary.org`), built on **httpx** and **pydantic**. It is a standalone, publishable package (PyPI: `databrarypy`) — *not* part of the `databrary-core` vendoring ecosystem. It talks to the API over HTTP the way any external consumer would: OAuth2 password-grant auth with automatic token refresh, retry/backoff, pagination, and binary downloads, with pydantic models covering users, volumes, sessions, folders, records, search, uploads, and system metadata.

- Python 3.12+, Poetry-managed.
- Versioned with **conventional commits** + **python-semantic-release** (auto-released from `main`/`staging` by CI).

## File Map

```
databrarypy/
├── src/databrarypy/
│   ├── __init__.py            # Public API surface: DatabraryClient + *Resource exports
│   ├── client.py              # DatabraryClient: construction, from_env(), headers, whoami()
│   ├── auth.py                # OAuth2Client: password grant at /o/token/, refresh, token state
│   ├── errors.py              # ApiError hierarchy (Unauthorized/Forbidden/NotFound/RateLimit/Server)
│   ├── resources/            # One class per API area — all extend _base.BaseResource
│   │   ├── _base.py           # Shared HTTP + retry/backoff + pagination (Page[T]) + normalization
│   │   ├── volumes.py, sessions.py, folders.py, records.py, users.py,
│   │   ├── institutions.py, search.py, tags.py, categories.py, funders.py,
│   │   ├── uploads.py, system.py, bulk.py
│   ├── models/                # pydantic models, one module per domain (snake_case payloads)
│   └── utils/
│       ├── case.py            # snake_keys / camel↔snake conversion
│       └── strings.py
├── tests/
│   ├── unit/                  # Offline tests (mocked transport) — what CI runs and gates coverage on
│   ├── integration/           # Live "staging" tests against a real API (marked @pytest.mark.staging)
│   ├── fixtures/              # Shared fixtures + canned API response data per domain
│   └── conftest.py
├── example/example.py         # Interactive records-management demo (reads example/.env)
├── Makefile                   # All dev commands (see Development)
├── pyproject.toml             # Poetry, ruff, mypy(strict), pytest, commitizen, semantic-release config
├── .pre-commit-config.yaml    # ruff, mypy, commitizen (commit-msg), hygiene hooks
└── docs/                      # pdoc-generated API docs (published by docs.yml workflow)
```

## Architecture in brief

- **`DatabraryClient`** owns a single `httpx.Client` and an `OAuth2Client`, and exposes one resource object per API area (`client.volumes`, `client.sessions`, …). Construct it directly or via `DatabraryClient.from_env(login=True)` reading `BASE_URL`/`CLIENT_ID`/`CLIENT_SECRET`/`USERNAME`/`PASSWORD` from a `.env`.
- **Auth**: call `client.auth.login()` once. Every request fetches headers via `get_valid_access_token()`, which transparently refreshes when within ~30s of expiry. A single long-lived client instance is the intended usage for hours/days-long scripts.
- **Resources** all extend `BaseResource`, which centralizes request execution, retry/backoff (with `Retry-After` support), key normalization, pagination (`page(...) → Page[T]`, `list(...)` iterates all), and download streaming.
- **Case normalization**: the API returns mostly camelCase, but the client normalizes to **snake_case by default** (`snake_case=True`), which is the shape the pydantic models expect.

## Do / Don't

**Layering**

- DON'T put HTTP/retry/pagination logic in individual resource classes — it belongs in `resources/_base.py`. Resource methods should be thin wrappers that call the base helpers and validate into a model.
- DO add a new endpoint as a method on the matching `*Resource`, returning a pydantic model from `models/`. Add a new resource class (and wire it into `client.py` + `__init__.py` `__all__`) only for a genuinely new API area.
- DO keep the public surface in `src/databrarypy/__init__.py` `__all__` in sync when adding/removing exported classes.

**Models & case**

- DO define request/response shapes as pydantic models in `models/` and expect **snake_case** input. If you ever set `snake_case=False`, normalize manually with `utils.case.snake_keys` before `model_validate`.
- DO keep models strict and typed — `mypy` runs in `--strict` mode over `src/`.

**Auth & errors**

- DON'T scatter token-refresh logic; it lives in `auth.py` / `get_valid_access_token()`. Resources must not manage tokens themselves.
- DO raise/propagate the typed exceptions in `errors.py` rather than bare `httpx` errors, so callers can catch by semantic class.

**Commits & releases**

- DO use conventional commits (`feat:`, `fix:`, `refactor:`, …) — commitizen enforces the format via the `commit-msg` hook, and `feat`/`fix`/`perf`/`refactor` drive automated semantic-release versioning. `make commit` walks you through one.
- DON'T hand-edit the version in `pyproject.toml` or `CHANGELOG.md`; releases are automated from commit history on `main`/`staging`.

**Secrets**

- DON'T commit credentials. `.env` and `example/.env` are gitignored — keep `CLIENT_SECRET`/`PASSWORD` out of git.

## Development & Testing

```bash
make install        # poetry install
make test           # unit tests only, coverage gated at 80% (what CI runs)
make coverage       # unit tests + coverage report with 80/90% thresholds
make lint           # ruff check src/ tests/
make format         # ruff --fix + ruff format
make type-check     # mypy --strict over src/
make pre-commit     # run all pre-commit hooks
make docs           # generate pdoc API docs into ./docs
```

- **Unit tests** (`tests/unit/`) run offline with mocked transport and are the CI gate — keep them fast and deterministic. New behavior needs unit coverage to stay above the 80% threshold.
- **Integration tests** (`tests/integration/`) are marked `@pytest.mark.staging` and hit a **real API**; `make test` deselects them by default. Run them deliberately with `make test-integration` and valid staging credentials. They create/rename/delete real resources, so treat them as outward-facing.
- CI (`.github/workflows/ci.yml`) runs lint + format check + mypy + unit coverage on Python 3.12 and 3.13, then auto-releases on push to `main`/`staging`.

## Key References

- [README.md](README.md) — onboarding, OAuth2 setup, quickstart, `from_env`, token-refresh behavior, example script
- [example/example.py](example/example.py) — interactive records-management walkthrough
- [pyproject.toml](pyproject.toml) — tooling config (ruff/mypy/pytest/commitizen/semantic-release)
- [databraryr](../databraryr/) — the sibling R client for the same API
- Databrary API: `https://api.databrary.org` (token endpoint `/o/token/`)
