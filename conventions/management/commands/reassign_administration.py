from django.core.management.base import BaseCommand, CommandParser
from django.db import models

from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--departements",
            required=True,
            help="List of the impacted departements",
            action="store",
            nargs="+",
        )
        parser.add_argument(
            "--new-admin-code",
            required=True,
            type=str,
            help="New administration to assign to the conventions (code)",
            action="store",
            nargs="?",
        )
        parser.add_argument(
            "--no-dry-run",
            default=False,
            action="store_true",
            help="Disable dry run mode",
        )
        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        self.stdout.write("Reassign administration command called")

        # Parse arguments
        departements = kwargs["departements"]
        new_admin = Administration.objects.get(code=kwargs["new_admin_code"])
        no_dry_run = kwargs["no_dry_run"]

        # Find the conventions assigned to current_admin
        programmes = Programme.objects.filter(
            code_insee_departement__in=departements
        ).exclude(administration=new_admin)
        conventions = Convention.objects.filter(programme__in=programmes)
        old_admins = (
            programmes.values("administration")
            .distinct()
            .annotate(count=models.Count("pk"))
        )

        # Output summary
        self.stdout.write("Summary before execution:")
        self.stdout.write("--------------------------")
        programmes_count = programmes.count()
        self.stdout.write(f"{programmes_count} programmes will be updated:")
        if programmes_count < 10:
            for p in programmes:
                self.stdout.write(f"    - {p.nom} - {p.numero_galion}")
        self.stdout.write("--------------------------")
        conventions_count = conventions.count()
        self.stdout.write(f"{conventions_count} conventions will be impacted:")
        if conventions_count < 10:
            for c in conventions:
                self.stdout.write("    - " + str(c))
        self.stdout.write("--------------------------")
        self.stdout.write("Current administrations for the impacted conventions:")
        for old_admin in old_admins:
            admin = Administration.objects.get(pk=old_admin["administration"])
            self.stdout.write(f"{admin.code} ({old_admin['count']} conventions)")

        if no_dry_run:
            # Update administration and save history
            for p in programmes:
                p.reassign_command_old_admin_backup = {
                    "backup_code": p.administration.code
                }
                p.administration = new_admin
                p.save()
            self.stdout.write("Changes executed")
        else:
            self.stdout.write(self.style.WARNING("Dry run mode, no changes executed"))
