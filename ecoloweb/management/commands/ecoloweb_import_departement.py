import sys
import datetime

from django.core.management import BaseCommand
from django.db import connections
from django.db import transaction

from tqdm import tqdm

from ecoloweb.services import ConventionImporter


class Command(BaseCommand):
    help = "Download data from an ecoloweb database"

    def add_arguments(self, parser):
        parser.add_argument(
            "departement",
            nargs=1,
            default=[],
            help="Départements on which restrict import of conventions",
        )
        parser.add_argument(
            "--use-transaction",
            action="store_true",
            help="Run queries inside a transaction",
        )
        parser.add_argument(
            "--debug", action="store_true", help="Print debug statement"
        )
        parser.add_argument("--setup", action="store_true", help="Force setup DB")
        parser.add_argument(
            "--no-progress",
            action="store_true",
            help="Disable progress bar, only print info into newlines",
        )

    def handle(self, *args, **options):
        if "ecoloweb" not in connections:
            print("No 'ecoloweb' connection defined, import aborted!")
            sys.exit(1)

        departement: str = options["departement"][0]
        import_date: datetime = datetime.datetime.today()
        use_transaction = options["use_transaction"]

        debug = options["debug"]
        setup = options["setup"]
        no_progress = options["no_progress"]

        transaction.set_autocommit(not use_transaction)
        progress = None

        try:
            importer = ConventionImporter(departement, import_date, debug=debug)
            importer.setup_db(force=setup)

            results = importer.get_all()
            # Progress bar
            if not no_progress:
                progress = tqdm(total=results.lines_total)
            # Actual processing
            for result in results:
                importer.process_result(result)
                self._on_result(progress, results)

        except BaseException as e:
            if use_transaction:
                print("Rollabcking all changes due to runtime error")
                transaction.rollback()
            if not isinstance(e, KeyboardInterrupt):
                raise e
        else:
            if progress is not None:
                progress.close()
            if use_transaction:
                transaction.commit()

    def _on_result(self, progress, results):
        if progress is not None:
            progress.update(1)
        else:
            print(
                f"Processed convention #{results.lines_fetched} (out of {results.lines_total} total)"
            )
