import sys
from django.core.management import BaseCommand
from django.db import connections
from django.db import transaction

from tqdm import tqdm

from ecoloweb.services import ConventionImporter


class Command(BaseCommand):
    help = 'Download data from an ecoloweb database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Do not persist downloaded data'
        )
        parser.add_argument(
            '--departements',
            nargs='*',
            default=[],
            help="Départements on which restrict import of conventions"
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Print debug statement'
        )

    def handle(self, *args, **options):
        if 'ecoloweb' not in connections:
            print("No 'ecoloweb' connection defined, migration aborted!")
            sys.exit(1)

        dry_run = options["dry_run"]
        debug = options["debug"]
        criteria = {}
        if len(options["departements"]) > 0:
            criteria['departements'] = [f"'{d}'" for d in options["departements"]]

        if dry_run:
            print("Running in dry mode")

        transaction.set_autocommit(False)
        progress = None

        try:
            importer = ConventionImporter(debug)
            results = importer.get_all_results(criteria)
            # Progress bar
            progress = tqdm(total=results.lines_total)
            # Actual processing
            for result in results:
                importer.process_result(result)
                progress.update(1)

        except Exception as e:
            transaction.rollback()

            print("Rollabcking all changes due to runtime error")
            raise e
        finally:
            if progress is not None:
                progress.close()
            if dry_run:
                transaction.rollback()
            else:
                transaction.commit()
