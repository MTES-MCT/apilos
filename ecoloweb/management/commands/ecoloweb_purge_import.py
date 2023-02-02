import sys
from typing import List

from django.conf import settings
from django.core.management import BaseCommand

from conventions.models import Convention
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
            "--purge-models",
            action="store_true",
            help="Also delete related APiLos models",
        )

    def handle(self, *args, **options):
        if settings.ENVIRONMENT == "production":
            print("This command can't be executed on prod environment")
            sys.exit(1)

        departements: List[str] = options["departements"]

        purge_models = options["purge_models"]

        if purge_models:
            convention_ids = EcoloReference.objects.values_list(
                "apilos_id", flat=True
            ).filter(
                departement__in=departements,
                apilos_model=EcoloReference.get_class_model_name(Convention),
            )

            Convention.objects.filter(id__in=convention_ids).delete()
            print(f"Purged {len(convention_ids)} convention(s)")

        EcoloReference.objects.filter(departement__in=departements).delete()
        print(
            f"Ecolo references linked to import on departement(s) {', '.join(departements)} deleted"
        )
