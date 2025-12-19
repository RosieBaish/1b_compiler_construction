#! /bin/bash

set -e

source .venv/bin/activate

uv run mypy *.py
uv run ruff check
uv run ruff format

uv run pytest --cov=.

uv run main.py
