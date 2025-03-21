from django.core.management.base import BaseCommand
from django.db.models import F
from django.db.models.functions import Left, Length

from programmes.models import Programme


class Command(BaseCommand):
    help = "Vérifie et corrige les codes INSEE departementaux"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="Run the command in dry run mode without making any changes",
        )

    def handle(self, *args, **options):
        queryset = (
            Programme.objects.exclude(code_insee_commune="")
            .annotate(code_insee_departement_len=Length("code_insee_departement"))
            .exclude(code_insee_departement_len=3)
            .annotate(dpt_code_from_insee_commune=Left("code_insee_commune", 2))
            .exclude(dpt_code_from_insee_commune=F("code_insee_departement"))
        )

        self.stdout.write(f"Nombre de programmes à corriger: {queryset.count()}")

        for programme in queryset:
            self.stdout.write(
                f"Programme {programme.id}, "
                f"commune: {programme.code_insee_commune}, "
                f"dpt: {programme.code_insee_departement} => {programme.dpt_code_from_insee_commune}"
            )
            if options["dryrun"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"Dry run: Programme {programme.id} non mis à jour"
                    )
                )
                continue

            programme.code_insee_departement = programme.dpt_code_from_insee_commune
            programme.save()
            self.stdout.write(
                self.style.SUCCESS(f"Programme {programme.id} mis à jour")
            )
