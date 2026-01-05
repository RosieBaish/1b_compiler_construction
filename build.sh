#! /bin/bash

set -e

source .venv/bin/activate

rm -f generated_*_parser.py

uv run mypy *.py
uv run ruff check
uv run ruff format

uv run pytest --cov=. tests/

uv run main.py --parser-generator

uv run mypy generated_*_parser.py
uv run ruff check generated_*_parser.py
uv run ruff format --diff generated_*_parser.py
uv run pytest --cov=. --cov-append tests_generated_code/

echo "=============================================================================================================="

uv run generated_g2_parser.py --source "x + y"

echo "=============================================================================================================="

uv run generated_slang_parser.py slang/fib.slang

echo "=============================================================================================================="
