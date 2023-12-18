#!make

fmt:
	pre-commit run --all-files

fmt-unstaged:
	pre-commit run --files $(shell git diff --name-only)

test:
	pytest -n auto --maxfail=3