import json
from typing import Any

from django.core.management import BaseCommand
from django.db.models import Count

from programmes.models import Programme
from programmes.utils import diff_programme_duplication


class Command(BaseCommand):
    help = "Analyse les doublons de programme"

    def list_duplicates(self) -> list[dict[str, Any]]:
        return list(
            Programme.objects.exclude(conventions__isnull=True)
            .filter(parent__isnull=False)
            .filter(numero_galion__regex=r"^\w{13}$")
            .values("numero_galion")
            .annotate(count=Count("numero_galion"))
            .filter(count__gt=1)
            .order_by("-count")
        )

    def handle(self, *args, **options):
        duplicates = self.list_duplicates()

        nb_diff = 0
        for duplicate in duplicates:
            diff = diff_programme_duplication(
                numero_operation=duplicate.get("numero_galion")
            )
            if len(diff):
                nb_diff += 1
                duplicate["diff"] = diff

        self.stdout.write(f"Nombre de doublons: {len(duplicates)}")
        self.stdout.write(f"Nombre de doublons avec diff: {nb_diff}")

        output_filepath = "/tmp/programme_duplicates.json"
        with open(output_filepath, "w") as f:
            f.write(json.dumps(duplicates, indent=2))

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Une liste des doublons a été crée dans: {output_filepath}"
            )
        )
