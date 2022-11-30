import sys
from typing import List

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connections
from django.db import transaction

from tqdm import tqdm

from ecoloweb.services import ConventionImporter


class Command(BaseCommand):
    help = 'Purge data from previous Ecoloweb import'

    def add_arguments(self, parser):
        parser.add_argument(
            'departements',
            nargs='?',
            default=[],
            help="Départements on which purge import data"
        )
        parser.add_argument(
            '--purge-models',
            action='store_true',
            help='Also delete related APiLos models'
        )

    def handle(self, *args, **options):
        if settings.ENVIRONMENT == "production":
            print("This command can't be executed on prod environment")
            sys.exit(1)

        departements: List[str] = options['departements']
        purge_models = options["purge_models"]

        # TODO implement action
