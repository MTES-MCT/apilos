import json

from django.core.management import BaseCommand
from siap.siap_client.client import SIAPClient


class Command(BaseCommand):
    help = "Display habilitations"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

        self.client = SIAPClient.get_instance()

    def add_arguments(self, parser):
        parser.add_argument(
            "cerbere_login",
            type=str,
            default=None,
            help="Identifian Cerbere de l'utilisateur",
        )

    def handle(self, *args, **options):
        print(
            json.dumps(
                self.client.get_habilitations(options["cerbere_login"]), indent=2
            )
        )
