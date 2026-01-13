.PHONY: help install dev test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run development server"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean cache files"

install:
	poetry install

dev:
	poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

test:
	poetry run pytest -v

lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run black .
	poetry run ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage
