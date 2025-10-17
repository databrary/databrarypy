.PHONY: help install test coverage lint format type-check clean all commit bump pre-commit test-integration integration-coverage

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests (excludes 'staging' by default)"
	@echo "  make coverage     - Run tests with coverage"
	@echo "  make test-integration      - Run only staging integration tests"
	@echo "  make integration-coverage - Run staging tests with coverage"
	@echo "  make lint         - Run ruff checks"
	@echo "  make format       - Format code with ruff and black"
	@echo "  make type-check   - Run mypy type checking"
	@echo "  make clean        - Remove cache and build files"
	@echo "  make all          - Run pre-commit on all files, then tests"
	@echo "  make pre-commit   - Run pre-commit hooks on all files"
	@echo "  make commit       - Create a conventional commit using commitizen"
	@echo "  make bump         - Bump version and update changelog"

install:
	poetry install

test:
	poetry run pytest tests/unit/ -v --cov=databrarypy --cov-report=term-missing

coverage:
	poetry run pytest tests/unit/ -v --cov=databrarypy --cov-report=term-missing --cov-report=json --cov-fail-under=80
	@COVERAGE=$$(poetry run python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])"); \
	echo "Coverage: $${COVERAGE}%"; \
	if [ $$(echo "$${COVERAGE} < 80" | bc -l) -eq 1 ]; then \
		echo "❌ Coverage is below 80% ($${COVERAGE}%)"; \
		exit 1; \
	elif [ $$(echo "$${COVERAGE} < 90" | bc -l) -eq 1 ]; then \
		echo "⚠️  Warning: Coverage is below 90% ($${COVERAGE}%)"; \
	else \
		echo "✅ Coverage is above 90% ($${COVERAGE}%)"; \
	fi

test-integration:
	poetry run pytest -s tests/integration

integration-coverage:
	poetry run pytest -s tests/integration --cov=databrarypy --cov-report=term-missing

lint:
	poetry run ruff check src/ tests/

format:
	poetry run ruff check --fix src/ tests/
	poetry run ruff format src/ tests/
	poetry run black src/ tests/

type-check:
	poetry run mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/ coverage.json

all: pre-commit test

pre-commit:
	poetry run pre-commit run --all-files

commit:
	poetry run cz commit

bump:
	poetry run cz bump
