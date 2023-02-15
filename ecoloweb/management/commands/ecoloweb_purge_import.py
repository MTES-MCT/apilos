import sys
from typing import List

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction

from ecoloweb.models import EcoloReference


class Command(BaseCommand):
    help = "Purge data from previous Ecoloweb import"

    def add_arguments(self, parser):
        parser.add_argument(
            "departements",
            nargs="+",
            default=[],
            help="Départements on which purge import data",
        )
        parser.add_argument(
            "--keep-models",
            action="store_true",
            help="Keep related APiLos models, do not delete",
        )

    def handle(self, *args, **options):
        if settings.ENVIRONMENT == "production":
            print("This command can't be executed on prod environment")
            sys.exit(1)

        departements: List[str] = options["departements"]
        keep_models = options["keep_models"]

        count = 0
        references = EcoloReference.objects.filter(departement__in=departements)
        transaction.set_autocommit(False)
        try:
            for reference in references:
                target = reference.resolve()
                if target is not None and not keep_models:
                    target.delete()
                reference.delete()
                count += 1
            print(
                f"Deleted {count} Ecolo reference(s) linked to import on departement(s) {', '.join(departements)} deleted"
            )
        except KeyboardInterrupt:
            transaction.rollback()
        else:
            transaction.commit()
