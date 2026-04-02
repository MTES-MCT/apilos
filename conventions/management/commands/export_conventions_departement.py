import openpyxl
from django.core.management.base import BaseCommand, CommandError
from django.http import HttpRequest
from openpyxl.styles import Font

from apilos_settings.models import Departement
from conventions.models import Convention
from conventions.services.utils import (
    get_convention_export_excel_header,
    get_convention_export_excel_row,
)


class Command(BaseCommand):
    help = (
        "Exporte toutes les conventions d'un département au format Excel. "
        "Exemple : python manage.py export_conventions_departement 79"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "departement",
            type=str,
            help="Code INSEE du département (ex: 79 pour Deux-Sèvres)",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Chemin du fichier de sortie (par défaut: conventions_<code>.xlsx)",
        )
        parser.add_argument(
            "--statut",
            type=str,
            default=None,
            help="Filtrer par statut (ex: Signée, Instruction, Projet...)",
        )

    def handle(self, *args, **options):
        code_departement = options["departement"]
        output = options["output"]
        statut = options["statut"]

        # Vérifier que le département existe
        try:
            departement = Departement.objects.get(code_insee=code_departement)
        except Departement.DoesNotExist as err:
            raise CommandError(
                f"Département avec le code INSEE '{code_departement}' introuvable. "
                "Vérifiez le code (ex: 79, 75, 971)."
            ) from err

        self.stdout.write(
            f"Export des conventions pour le département "
            f"{departement.nom} ({code_departement})..."
        )

        conventions = (
            Convention.objects.filter(
                programme__code_insee_departement=code_departement,
            )
            .select_related(
                "parent",
                "programme",
                "programme__bailleur",
                "programme__administration",
            )
            .prefetch_related(
                "lots",
                "lots__logements",
            )
            .order_by("programme__ville", "numero")
        )

        if statut:
            conventions = conventions.filter(statut=statut)

        count = conventions.count()
        if count == 0:
            self.stdout.write(
                self.style.WARNING("Aucune convention trouvée pour ce département.")
            )
            return

        self.stdout.write(f"{count} convention(s) trouvée(s).")

        # Générer le fichier Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Conventions"

        # Écrire l'en-tête
        request = HttpRequest()
        headers = get_convention_export_excel_header(request)
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        exported = 0
        errors = 0
        for convention in conventions.iterator(chunk_size=1000):
            try:
                row = get_convention_export_excel_row(request, convention)
                ws.append(row)
                exported += 1
            except (AttributeError, ValueError, TypeError) as e:
                errors += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Erreur pour la convention {convention.uuid}: {e}"
                    )
                )

        if not output:
            output = f"conventions_{code_departement}.xlsx"

        wb.save(output)

        self.stdout.write(
            self.style.SUCCESS(f"{exported} convention(s) exportée(s) dans '{output}'.")
        )
        if errors:
            self.stdout.write(
                self.style.WARNING(f"{errors} convention(s) en erreur (ignorées).")
            )
