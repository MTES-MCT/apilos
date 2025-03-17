#!make

SHELL := /bin/bash
DJANGO_ADMIN := @python manage.py
DB_URL := postgres://apilos:apilos@localhost:5433/apilos# pragma: allowlist secret

server:
	@python manage.py runserver 0.0.0.0:8001

worker:
	@python -m celery -A core.worker worker -B -l INFO

fmt:
	@pre-commit run --all-files

fmt-unstaged:
	@pre-commit run --files $(shell git diff --name-only)

test:
	@pytest -n auto --maxfail=3

freeze-requirements:
	@pip-compile --resolver=backtracking requirements.in --generate-hashes
	@pip-compile --resolver=backtracking dev-requirements.in --generate-hashes

run-all:
	rm -rf .parcel-cache
	honcho start -f Procfile.dev

db-restore:
	mkdir -p tmpbackup
	scalingo --app apilos-siap-production --addon postgresql backups-download --output tmpbackup/backup.tar.gz
	tar xfz tmpbackup/backup.tar.gz --directory tmpbackup
	@DUMP_FILE=$$(find tmpbackup -type f -name "*.pgsql" -print -quit); \
	for table in $$(psql "$(DB_URL)" -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public'"); do \
	    psql "$(DB_URL)" -c "DROP TABLE IF EXISTS $$table CASCADE"; \
	done || true
	@DUMP_FILE=$$(find tmpbackup -type f -name "*.pgsql" -print -quit); \
	pg_restore -d "$(DB_URL)" --clean --no-acl --no-owner --no-privileges "$$DUMP_FILE" || true
	rm -rf tmpbackup
	$(DJANGO_ADMIN) migrate
