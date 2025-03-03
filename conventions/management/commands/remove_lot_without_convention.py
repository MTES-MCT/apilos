from django.core.management.base import BaseCommand
from django.db.models import Count

from programmes.models import Lot


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
            Lot.objects.all()
            .annotate(convention_count=Count("conventions"))
            .filter(convention_count=0)
        )

        lots_count = lots.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Found {lots_count} lots without conventions to be removed: "
            )
        )
        for lot in lots:
            self.stdout.write(
                self.style.SUCCESS(
                    f" - {lot.convention.programme.nom}"
                    f" - {lot.convention.programme.numero_operation}"
                    f" - {lot.financement} - {lot.cree_le}"
                )
            )

        if not dry_run:
            count = 0
            for lot in lots:
                lot.delete()
                count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Removed {count}/{lots_count} lots without conventions"
                )
            )
