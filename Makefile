#!make

SHELL := /bin/bash

fmt:
	@pre-commit run --all-files

fmt-unstaged:
	@pre-commit run --files $(shell git diff --name-only)

test:
	@pytest -n auto --maxfail=3

freeze-requirements:
	@pip-compile --resolver=backtracking requirements.in --generate-hashes
	@pip-compile --resolver=backtracking dev-requirements.in --generate-hashes
