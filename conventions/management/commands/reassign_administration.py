import logging
from datetime import datetime

from django.core.management.base import BaseCommand, CommandParser

from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--perimeter",
            required=True,
            help="List of the impacted codes postaux",
            action="store",
            nargs="+",
        )
        parser.add_argument(
            "--start-date",
            required=True,
            help="Creation date YYYY-MM-DD from which to reassign conventions",
            action="store",
            nargs=1,
        )
        parser.add_argument(
            "--end-date",
            required=True,
            help="Creation date YYYY-MM-DD until which to reassign conventions",
            action="store",
            nargs=1,
        )
        parser.add_argument(
            "--current-admin-code",
            required=True,
            help="Administration currently assigned to the conventions (code)",
            action="store",
            nargs=1,
        )
        parser.add_argument(
            "--new-admin-code",
            required=True,
            help="New administration to assign to the conventions (code)",
            action="store",
            nargs=1,
        )
        parser.add_argument(
            "--dry-run", type=bool, help="Dry run mode", nargs="?", default=True
        )
        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        self.stdout.write("Reassign administration command called")

        # Parse arguments
        codes_postaux = kwargs["perimeter"]
        start_date = datetime.strptime(kwargs["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(kwargs["end_date"], "%Y-%m-%d").date()
        current_admin = Administration.objects.get(code=kwargs["current_admin_code"])
        new_admin = Administration.objects.get(code=kwargs["new_admin_code"])
        dry_run = kwargs["dry_run"]

        # Find the conventions assigned to current_admin
        programmes = Programme.objects.filter(
            administration=current_admin, code_postal__in=codes_postaux
        )
        conventions = Convention.objects.filter(programme__in=programmes)

        # Filter the conventions to be in the date range
        conventions = conventions.filter(cree_le__range=[start_date, end_date])

        # Get programs to udpate
        programmes_filtered = Programme.objects.filter(
            id__in=conventions.values_list("programme_id")
        )

        # Get the list of conventions not in range but attached to thesse programmes to warn user
        conventions_also_impacted = Convention.objects.filter(
            programme__in=programmes_filtered
        ).exclude(id__in=conventions.values_list("id"))

        self.stdout.write("Summary before execution:")
        self.stdout.write("--------------------------")
        self.stdout.write(f"{programmes_filtered.count()} programmes will be updated:")
        for p in programmes_filtered:
            self.stdout.write(f"    - {p.nom} - {p.numero_galion}")
        self.stdout.write("--------------------------")
        self.stdout.write(
            f"{conventions.count()} conventions in the date range will be impacted:"
        )
        for c in conventions:
            self.stdout.write("    - " + str(c))
        self.stdout.write("--------------------------")
        if conventions_also_impacted.count() > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"WARNING {conventions_also_impacted.count()} conventions out of "
                    f"the date range will be impacted as a side-effect:"
                )
            )
            for c in conventions_also_impacted:
                self.stdout.write("    - " + str(c))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run mode, no changes executed"))
        else:
            # Update administration and save history
            now = datetime.now()
            for p in programmes_filtered:
                p.administration = new_admin
                p._change_reason = (
                    f"Reassign administration command launched on {str(now)}"
                )
                p.save()
            self.stdout.write("Changes executed")
