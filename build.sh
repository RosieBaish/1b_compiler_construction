#! /bin/bash

set -e

source .venv/bin/activate

rm -f generated_*_parser.py

uv run mypy *.py
uv run ruff check
uv run ruff format

uv run pytest --cov=. tests/

uv run main.py --parser-generator

uv run pytest --cov=. --cov-append tests_generated_code/
