import logging

from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer

from conventions.models import Convention, ConventionStatut
from programmes.api.operation_serializers import ConventionInfoSIAPSerializer

# Accéder aux données sérialisées

# Récupérer un objet Programme


class Command(BaseCommand):
    def handle(self, *args, **options):
        conventions = (
            Convention.objects.filter(
                statut__in=[
                    ConventionStatut.A_SIGNER.label,
                    ConventionStatut.SIGNEE.label,
                ]
            )
            .prefetch_related(
                "programme",
                "programme__bailleur",
                "programme__administration",
                "lot",
                "lot__logements__annexes",
                "prets",
            )
            .order_by("numero", "-cree_le")
            .distinct("numero")
        )
        count = conventions.count()

        with open("conventions.json", "w", newline="") as jsonfile:
            offset = 0
            while offset < count:
                logging.warning("count %i, offset %i", count, offset)
                for convention in conventions[offset : offset + 1000]:
                    serializer = ConventionInfoSIAPSerializer(convention)
                    json_data = JSONRenderer().render(serializer.data).decode("utf-8")
                    jsonfile.write(json_data)
                    jsonfile.write("\n")
                offset += 1000
