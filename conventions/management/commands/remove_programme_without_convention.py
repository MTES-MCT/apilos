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

        programmes = (
            Programme.objects.all()
            .annotate(convention_count=Count("conventions"))
            .filter(convention_count=0)
        )

        programmes_count = programmes.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {programmes_count} programmes without conventions to be removed: "
            )
        )
        for programme in programmes:
            self.stdout.write(
                self.style.SUCCESS(
                    f" - {str(programme.uuid)} - {programme.nom} - {programme.numero_galion} - {programme.cree_le}"
                )
            )

        if not dry_run:
            count = 0
            for programme in programmes:
                programme.delete()
                count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Removed {count}/{programmes_count} programmes without conventions"
                )
            )
