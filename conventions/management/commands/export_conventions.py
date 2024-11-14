import argparse

from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer

from conventions.models import Convention, ConventionStatut
from programmes.api.operation_serializers import ConventionInfoSIAPSerializer

# Accéder aux données sérialisées

# Récupérer un objet Programme


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            help="limit the number of convention to export",
            type=int,
            default=None,
        )
        parser.add_argument(
            "--with-ended",
            help="Run command and write changes to the database",
            action=argparse.BooleanOptionalAction,
            default=False,
        )

    def handle(self, *args, **options):
        nb_conventions = options.get("limit")
        with_ended = options.get("with_ended")
        status_to_export = [
            ConventionStatut.A_SIGNER.label,
            ConventionStatut.SIGNEE.label,
        ]
        if with_ended:
            status_to_export.append(ConventionStatut.RESILIEE.label)
            status_to_export.append(ConventionStatut.DENONCEE.label)

        conventions = (
            Convention.objects.filter(statut__in=status_to_export)
            .prefetch_related(
                "parent",
                "programme",
                "programme__bailleur",
                "programme__administration",
                # "lot",
                # "lot__logements__annexes",
                # "lot__prets",
            )
            .order_by("numero", "-cree_le")
            .distinct("numero")
        )
        if nb_conventions:
            conventions = conventions[:nb_conventions]
        count = conventions.count()

        with open("conventions.json", "w", newline="") as jsonfile:
            offset = 0
            while offset < count:
                self.stdout.write(f"count: {count}, offset: {offset}")
                for convention in conventions[offset : offset + 1000]:
                    serializer = ConventionInfoSIAPSerializer(convention)
                    json_data = JSONRenderer().render(serializer.data).decode("utf-8")
                    jsonfile.write(json_data)
                    jsonfile.write("\n")
                offset += 1000
