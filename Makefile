export PYTHONPATH=$(CURDIR)/src

all: lint test

clean:
	rm -f .coverage
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

format:
	uv run ruff format src tests
	uv run ruff check src tests --select I --fix

install:
	uv sync

install-test: install
	uv sync --group test

lint: lint-ruff lint-mypy

lint-ruff:
	uv run ruff check src tests
	uv run ruff format --check src tests

lint-mypy:
	uv run mypy src
	uv run mypy tests

test:
	uv run pytest tests/unit tests/integration --cov=engineering_assistant
