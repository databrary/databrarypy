# databrarypy

Python client library for the Databrary API

## Installation

```bash
pip install databrarypy
```

## Development

This project uses Poetry for dependency management.

### Quick Start

```bash
# Install dependencies
poetry install

# Install pre-commit hooks (optional but recommended)
poetry run pre-commit install

# Run all checks (format, lint, type-check, test)
make all
```

### Available Commands

```bash
# Run tests with coverage
make test
# or: poetry run pytest tests/ -v --cov=databrarypy

# Format code (ruff + black)
make format
# or: poetry run ruff format src/ tests/

# Lint code (ruff + mypy)
make lint
# or: poetry run ruff check src/ tests/

# Type checking (mypy)
make type-check
# or: poetry run mypy src/

# Clean cache files
make clean
```

### Linting & Code Quality

This project uses:
- **Ruff** - Fast Python linter (replaces flake8, isort, and more)
- **Black** - Code formatter
- **Mypy** - Static type checker
- **Commitizen** - Standardized commit messages and versioning
- **Pre-commit** - Git hooks for automatic checks

Pre-commit hooks will automatically run formatters and linters before each commit.

### Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Use Commitizen to create properly formatted commits:

```bash
# Instead of 'git commit -m "message"', use:
cz commit
# or
git cz

# Bump version and generate changelog
cz bump

# Generate changelog
cz changelog
```

**Commit types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Usage

```python
from databrarypy import DatabraryClient

# Initialize the client
client = DatabraryClient(
    base_url="https://nyu.databrary.org",
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent"
)

# Authenticate
client.auth.login_with_password("user@example.com", "password")

# Use the API
stats = client.system.get_db_stats()
print(f"Institutions: {stats.institutions}")
```

## License

MIT
