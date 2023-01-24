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
            "--no-transaction",
            action="store_true",
            help="Perform queries under transaction",
        )
        parser.add_argument(
            "--debug", action="store_true", help="Print debug statement"
        )
        parser.add_argument(
            "--no-progress",
            action="store_true",
            help="Disable progress bar, only print info into newlines",
        )

    def handle(self, *args, **options):
        if "ecoloweb" not in connections:
            print("No 'ecoloweb' connection defined, migration aborted!")
            sys.exit(1)

        departement: str = options["departement"][0]
        import_date: datetime = datetime.datetime.today()
        no_transaction = options["no_transaction"]

        debug = options["debug"]
        no_progress = options["no_progress"]

        transaction.set_autocommit(no_transaction)
        progress = None

        try:
            importer = ConventionImporter(departement, import_date, debug)
            results = importer.get_all()
            # Progress bar
            if not no_progress:
                progress = tqdm(total=results.lines_total)
            # Actual processing
            for result in results:
                importer.process_result(result, True)
                if progress is not None:
                    progress.update(1)
                else:
                    print(
                        f"Processed convention #{results.lines_fetched} (out of {results.lines_total} total)"
                    )

        except Exception as e:
            if not no_transaction:
                print("Rollabcking all changes due to runtime error")
                transaction.rollback()

            raise e
        else:
            if progress is not None:
                progress.close()
            if not no_transaction:
                transaction.commit()
