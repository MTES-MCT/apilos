import json
from pprint import pformat

from django.core.management import BaseCommand

from siap.siap_client.client import SIAPClient


class Command(BaseCommand):
    help = "Inspecte les données d'une opération SIAP"

    def add_arguments(self, parser):
        parser.add_argument(
            "--login",
            help="Cerbere login (votre email @beta.gouv.fr)",
            required=True,
        )
        parser.add_argument(
            "--habilitation-id",
            type=int,
            help="Habilitation ID",
            required=True,
        )
        parser.add_argument(
            "--operation",
            help="Numéro d'opération",
            required=True,
        )

    def handle(self, *args, **options):
        cerbere_login = options.get("login")
        habilitation_id = options.get("habilitation-id")
        numero_operation = options.get("operation")

        siap_operation = SIAPClient.get_instance().get_operation(
            user_login=cerbere_login,
            habilitation_id=habilitation_id,
            operation_identifier=numero_operation,
        )

        self.stdout.write(pformat(siap_operation, indent=2))

        output_filepath = f"/tmp/siap_operation_{numero_operation}.json"
        with open(output_filepath, "w") as f:
            f.write(json.dumps(siap_operation, indent=2))

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Opération SIAP {numero_operation} enregistrée dans {output_filepath}"
            )
        )
