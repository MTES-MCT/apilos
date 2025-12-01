import json

from django.core.management.base import BaseCommand
from django.db.models import Q

from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme


class Command(BaseCommand):
    help = "Update programme administration based on conventions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--conventions",
            type=str,
            required=True,
            help="Path to JSON file containing a list of convention numeros",
        )
        parser.add_argument(
            "--new_administration",
            type=str,
            required=True,
            help="Name of the new administration",
        )
        parser.add_argument(
            "--old_administration",
            type=str,
            required=True,
            help="Name of the old administration",
        )
        parser.add_argument(
            "--run",
            action="store_true",
            help="Apply changes to the database. Default is dry run.",
        )

    def handle(self, *args, **options):
        # Parse arguments
        conventions_path = options["conventions"]
        new_admin_name = options["new_administration"]
        old_admin_name = options["old_administration"]
        run = options["run"]

        # Load conventions from JSON file
        try:
            with open(conventions_path) as file:
                convention_numeros = json.load(file)
        except FileNotFoundError:
            self.stderr.write(f"Conventions file '{conventions_path}' not found.")
            return
        except json.JSONDecodeError:
            self.stderr.write(
                f"Conventions file '{conventions_path}' is not a valid JSON file."
            )
            return

        # Validate administrations
        try:
            new_admin = Administration.objects.get(nom=new_admin_name)
        except Administration.DoesNotExist:
            self.stderr.write(f"New administration '{new_admin_name}' does not exist.")
            return

        try:
            old_admin = Administration.objects.get(nom=old_admin_name)
        except Administration.DoesNotExist:
            self.stderr.write(f"Old administration '{old_admin_name}' does not exist.")
            return

        # Query conventions
        conventions_prob = Convention.objects.filter(
            (
                Q(numero__in=convention_numeros)
                | Q(parent__numero__in=convention_numeros)
            )
            & Q(programme__administration=old_admin)
        )

        if not conventions_prob.exists():
            self.stdout.write("No conventions found matching the given numeros.")
            return

        conventions_prob_numeros = set(
            conventions_prob.values_list("numero", flat=True)
        )
        programme_prob = Programme.objects.filter(
            conventions__in=conventions_prob
        ).distinct()

        # Process each convention
        for programme in programme_prob:
            # Check if the programme contains only conventions in conventions_prob
            programme_conventions = programme.conventions.all()
            programme_convention_numeros = set(
                programme_conventions.values_list("numero", flat=True)
            )

            if programme_convention_numeros.issubset(conventions_prob_numeros):
                # Update programme administration
                if programme.administration == old_admin:
                    if run:
                        programme.administration = new_admin
                        programme.save()
                        self.stdout.write(
                            f"Updated administration for programme '{programme.nom}' "
                            f"to '{new_admin_name}'."
                        )
                    else:
                        self.stdout.write(
                            f"[Dry Run] Updated administration for programme '{programme.nom}' "
                            f"to '{new_admin_name}'."
                        )
                else:
                    self.stderr.write(
                        f"Programme '{programme.nom}' does not belong to the old administration '{old_admin_name}'."
                    )
            else:
                self.stderr.write(
                    f"Skipped programme '{programme.numero_operation}' because "
                    f"contains other conventions not in the provided list."
                )
