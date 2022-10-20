import sys
from django.core.management import BaseCommand
from django.db import connections, DatabaseError
from django.db import transaction
from ecoloweb.services import EcolowebImportService


class Command(BaseCommand):
    help = 'Download data from an ecoloweb database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.importer = EcolowebImportService()

    def add_arguments(self, parser):
        parser.add_argument("--dry-run",
                            action='store_true',
                            help='Do not persist downloaded data'
                            )

    def handle(self, *args, **options):
        if 'ecoloweb' not in connections:
            print("No 'ecoloweb' connection defined, migration aborted!")
            sys.exit(1)

        dry_run = options["dry_run"]

        if dry_run:
            print("Running in dry mode")

        transaction.set_autocommit(False)

        try:
            # Actual processing
            ConventionImportHandler().import_all()
        except DatabaseError as e:
            transaction.rollback()
            raise e
        finally:
            if dry_run:
                transaction.rollback()
            else:
                transaction.commit()
