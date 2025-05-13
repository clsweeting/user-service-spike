# Makefile

.PHONY: help install lint typecheck test format check

help:
	@echo "Usage:"
	@echo "  make install      Install dependencies with poetry"
	@echo "  make lint         Run Ruff for linting"
	@echo "  make typecheck    Run Mypy for static typing"
	@echo "  make test         Run tests with pytest"
	@echo "  make format       Auto-format with black and isort"
	@echo "  make check        Run lint + typecheck + tests"

install:
	poetry install

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy .

test:
	poetry run pytest --maxfail=1 --disable-warnings -v

format:
	poetry run black .
	poetry run isort .

check: lint typecheck test
