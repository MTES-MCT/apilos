import sys
from datetime import date

from django.core.management import BaseCommand
from django.db import connections, transaction
from tqdm import tqdm

from ecoloweb.services import ConventionImporter


class Command(BaseCommand):
    help = "Download data from an ecoloweb database"

    def add_arguments(self, parser):
        parser.add_argument(
            "departements",
            nargs="+",
            type=str,
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
            "--update", action="store_true", help="Enable models update mode"
        )
        parser.add_argument(
            "--no-progress",
            action="store_true",
            help="Disable progress bar, only print info into newlines",
        )

    def handle(self, *args, **options):  # noqa: C901
        if "ecoloweb" not in connections:
            self.stdout.write("No 'ecoloweb' connection defined, import aborted!")
            sys.exit(1)

        departements: list = options["departements"]
        import_date: date = date.today()
        use_transaction = options["use_transaction"]

        debug = options["debug"]
        setup = options["setup"]
        update = options["update"]
        no_progress = options["no_progress"]

        transaction.set_autocommit(not use_transaction)
        progress = None

        try:
            for index, departement in enumerate(departements):
                importer = ConventionImporter(
                    departement, import_date, debug=debug, update=update
                )
                # Installation uniquement pour le premier département, sans quoi
                # la matview tombe et les autres processes tombent
                if setup and index == 0:
                    importer.setup_db()

                results = importer.get_all()
                # Progress bar
                if not no_progress:
                    progress = tqdm(total=results.lines_total)
                # Actual processing
                for result in results:
                    convention = importer.import_one(result["id"])
                    self._on_result(departement, convention, progress, results)

        except KeyboardInterrupt:
            if use_transaction:
                self.stdout.write("Rollabcking all changes due to runtime error")
                transaction.rollback()
        except BaseException as e:
            if use_transaction:
                self.stdout.write("Rollabcking all changes due to runtime error")
                transaction.rollback()
            raise e
        else:
            if progress is not None:
                progress.close()
            if use_transaction:
                transaction.commit()

    def _on_result(self, departement, convention, progress, results):
        if progress is not None:
            progress.update(1)
        else:
            pct = round(results.lines_fetched / results.lines_total * 100, 1)
            label = f"#{convention.id}" if convention is not None else "<ref supprimée>"
            self.stdout.write(
                f"({departement}) traité convention {label} "
                f"({results.lines_fetched} / {results.lines_total} => "
                f"{pct} %)"
            )
