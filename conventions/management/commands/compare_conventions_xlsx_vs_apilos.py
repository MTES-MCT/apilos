from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from conventions.models.convention import Convention


def _number_for_search(number):
    if not number or not isinstance(number, str):
        return False
    return (
        number.replace(" ", "")
        .replace("-", "")
        .replace(".", "")
        .replace(":", "")
        .replace("_", "")
    )


class Command(BaseCommand):
    help = """
Read the xlsx file of exhaustive list of conventions and compare with the
conventions in the database
"""

    def _should_continue(self):
        self.stdout.write(
            self.style.NOTICE(
                f"""
Lecture du fichier : {self.conv_file}
Pour le département : {self.department}
Feuille de calcule à interpréter : {self.input_sheetname}
Feuille de calcule contenant le résultat : {self.output_sheetname}
(Si une feuille de calcule `{self.output_sheetname}` existe, elle sera ré-initialisée)
Feuille de calcule contenant les indicateurs globales : {self.metadata_sheetname}
(Si une feuille de calcule `{self.metadata_sheetname}` existe, elle sera ré-initialisée)
                """
            )
        )

        while True:
            result = input("continuer ? (y/n)")
            if result.lower() == "n":
                self.stdout.write(
                    self.style.NOTICE(
                        "Vous avez choisi de stopper l'execution de cette commande"
                    )
                )
                exit(1)
            if result.lower() == "y":
                break

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Convention exhauustive list",
        )

    def handle(self, *args, **options):
        self.conv_file = options["file"]
        self.department = 79
        self.input_sheetname = "Sheet1"
        self.output_sheetname = "Resultats"
        self.metadata_sheetname = "Metadonnées"

        # Init metadata
        nb_with_field = "Nombre de conventions avec numéro"
        nb_found = "Nombre de conventions avec numéro trouvé"
        nb_in_db = "Nombre de conventions dans la base de données"

        metadata = {nb_with_field: 0, nb_found: 0, nb_in_db: 0}

        # Init fields from workbook
        # Only those fields will be reported in output sheet
        header_mapping = {
            "numero": "N°convention",
            "annee": "Année convention",
            "ville": "Communes",
            "bailleur": "Bailleurs",
            "avenant": "Avenant oui/non",
            "nom": "Nom de l’opération",
            "financement": "financement",
            # "bb":"Type  de Construction",
            "adresse": "Adresse",
            "nb_lgts": "Nb de logts",
        }
        header_result = {
            "numero": "Numero dans APiLos",
            "financement": "Financment dans APiLos",
            "nb_lgts": "Nb de lgts dans APiLos",
        }

        success_fill = PatternFill(
            start_color="92D050", end_color="92D050", fill_type="solid"
        )
        # warning_fill = PatternFill(
        #     start_color="FFA500", end_color="FFA500", fill_type="solid"
        # )
        error_fill = PatternFill(
            start_color="FF0000", end_color="FF0000", fill_type="solid"
        )

        convention_qs = Convention.objects.filter(
            parent_id__isnull=True
        ).prefetch_related("lots", "programme")

        # Display what the command will do
        self._should_continue()

        # Get input and output workbook sheets
        try:
            conv_workbook = load_workbook(filename=self.conv_file, data_only=True)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"le fichier {self.conv_file} n'existe pas")
            )
            exit(1)

        for sheetname in [self.output_sheetname, self.metadata_sheetname]:
            if sheetname in conv_workbook:
                del conv_workbook[sheetname]
            conv_workbook.create_sheet(sheetname)

        output_wb_sheet = conv_workbook[self.output_sheetname]
        metadata_wb_sheet = conv_workbook[self.metadata_sheetname]

        try:
            input_wb_sheet = conv_workbook[self.input_sheetname]
        except KeyError:
            self.stdout.write(
                self.style.ERROR(
                    f"la feuille de calcule {self.input_sheetname} n'existe pas"
                    f" dans le fichier {self.conv_file}"
                )
            )
            exit(1)

        column_from_index = {}
        # read the first row (header)
        for first_row in input_wb_sheet.iter_rows(min_row=1, max_row=1):
            for cell in first_row:
                #                if cell.value in header_mapping.values():
                column_from_index[cell.column] = cell.value
        self.stdout.write(f" Entêtes : {column_from_index.values()}")

        # for col, value in column_from_index.items():
        #     output_wb_sheet.cell(row=1, column=col, value=value)

        column_nb = 1
        for header in header_mapping.values():
            output_wb_sheet.cell(row=1, column=column_nb, value=header)
            column_nb += 1

        for header in header_result.values():
            output_wb_sheet.cell(row=1, column=column_nb, value=header)
            column_nb += 1

        for row in input_wb_sheet.iter_rows(min_row=2):
            convention = {}
            column_nb = 1
            row_nb = 0
            for cell in row:
                row_nb = cell.row
                convention[column_from_index[cell.column]] = cell.value
                if column_from_index[cell.column] in header_mapping.values():
                    output_wb_sheet.cell(
                        row=cell.row, column=column_nb, value=cell.value
                    )
                    column_nb += 1
            if numero := _number_for_search(convention[header_mapping["numero"]]):
                metadata[nb_with_field] += 1

                # found it in DB
                convention_from_db = convention_qs.filter(
                    numero_pour_recherche=numero
                ).first()
                if convention_from_db:
                    metadata[nb_found] += 1

                    for field in header_result.keys():
                        cell = output_wb_sheet.cell(
                            row=row_nb,
                            column=column_nb,
                            value=getattr(convention_from_db, field),
                        )
                        column_nb += 1
                        if convention[header_mapping[field]] == getattr(
                            convention_from_db, field
                        ):
                            cell.fill = success_fill
                        else:
                            cell.fill = error_fill

        metadata[nb_in_db] = Convention.objects.filter(
            programme__code_insee_departement=self.department, parent_id__isnull=True
        ).count()
        row = 1
        for kpi, value in metadata.items():
            metadata_wb_sheet.cell(row=row, column=1, value=kpi)
            metadata_wb_sheet.cell(row=row, column=2, value=value)
            row += 1

        conv_workbook.save(filename=self.conv_file)
