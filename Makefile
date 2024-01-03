#!make

SHELL := /bin/bash

fmt:
	@pre-commit run --all-files

fmt-unstaged:
	@pre-commit run --files $(shell git diff --name-only)

test:
	@pytest -n auto --maxfail=3

pip-compile:
	@pip-compile --resolver=backtracking requirements.in --generate-hashes
	@pip-compile --resolver=backtracking dev-requirements.in --generate-hashes

py-install:
	@if [ -d ".venv" ]; then source .venv/bin/activate && deactivate && rm -rf .venv; fi
	@python -m venv .venv
	@source .venv/bin/activate
	@pip install -r requirements.txt -r dev-requirements.txt

py-upgrade: pip-compile py-install
