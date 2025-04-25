from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer

from conventions.models import Convention
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

    def handle(self, *args, **options):
        nb_conventions = options.get("limit")

        conventions = (
            Convention.objects.prefetch_related(
                "parent",
                "avenant_types",
                "programme",
                "programme__bailleur",
                "programme__administration",
                "lots",
                "lots__logements__annexes",
                "lots__prets",
            )
            .order_by("uuid")
            .distinct("uuid")
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
