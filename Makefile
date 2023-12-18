#!make

fmt:
	@pre-commit run --all-files

fmt-unstaged:
	@pre-commit run --files $(shell git diff --name-only)

pip-compile:
	@pip-compile -o requirements.txt pyproject.toml
	@pip-compile --extra dev -o dev-requirements.txt pyproject.toml

pip-install:
	@pip install -r requirements.txt -r dev-requirements.txt
