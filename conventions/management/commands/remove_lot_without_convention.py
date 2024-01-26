from django.core.management.base import BaseCommand
from django.db.models import Count

from programmes.models import Programme


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            help="Dry run",
            action="store_true",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")

        lots = (
            Programme.objects.all()
            .annotate(convention_count=Count("conventions"))
            .filter(convention_count=0)
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {lots.count()} lots without conventions to be removed: "
            )
        )
        for lot in lots:
            self.stdout.write(
                self.style.SUCCESS(
                    f" - {lot.nom} - {lot.numero_galion} - {lot.cree_le}"
                )
            )

        if not dry_run:
            for lot in lots:
                lot.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Removed {lots.count()} lots without conventions")
            )
