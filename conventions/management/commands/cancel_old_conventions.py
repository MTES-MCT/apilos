from django.core.management.base import BaseCommand

from conventions.models import Convention
from conventions.models.choices import ConventionStatut


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--departement",
            help="Departement to cancel conventions for",
            action="store",
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "--administration_code",
            help="Administration code to cancel conventions for",
            action="store",
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "--older_than",
            help="Departement to cancel conventions for",
            action="store",
            nargs="?",
            default="2013-01-01",
        )

    def handle(self, *args, **options):
        departement = options.get("departement")
        administration_code = options.get("administration_code")
        if not departement and not administration_code:
            self.stdout.write(
                self.style.ERROR(
                    "You must provide a departement or an administration code"
                )
            )
            return

        older_than = options.get("older_than")
        conventions = Convention.objects.filter(
            programme__date_achevement__lt=older_than,
            statut=ConventionStatut.INSTRUCTION.label,
        )
        if departement:
            conventions = conventions.filter(
                programme__code_insee_departement=departement
            )
        if administration_code:
            conventions = conventions.filter(
                programme__administration__code=administration_code
            )

        nb_conventions = conventions.count()
        for convention in conventions:
            self.stdout.write(
                f" {convention.uuid} - {convention} - {convention.programme.date_achevement}"
            )

        go = input(
            f"{nb_conventions} conventions older than {older_than} will be canceled,"
            + " are you sure (No/yes)?"
        )

        if go.lower() == "yes":
            conventions.update(statut=ConventionStatut.ANNULEE.label)
            self.stdout.write(
                self.style.SUCCESS(f"{nb_conventions} conventions canceled")
            )
        else:
            self.stdout.write(self.style.NOTICE("Abording"))
