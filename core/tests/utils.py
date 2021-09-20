import datetime
from io import BytesIO
from openpyxl import load_workbook
from django.conf import settings
from bailleurs.models import Bailleur
from programmes.models import Programme

def create_bailleur():
    return Bailleur.objects.create(
        nom="3F",
        siret="12345678901234",
        capital_social="123000.50",
        ville="Marseille",
        dg_nom="Patrick Patoulachi",
        dg_fonction="PDG",
        dg_date_deliberation=datetime.date(2014, 10, 9),
    )

def create_programme(bailleur):
    return Programme.objects.create(
        nom="3F",
        bailleur = bailleur,
        code_postal = "75007",
        ville = "Paris",
        adresse = "22 rue segur",
        departement = 75,
        numero_galion = "12345",
        annee_gestion_programmation = 2018,
        zone_123 = 3,
        zone_abc = 'B1',
        surface_utile_totale = 5243.21,
        nb_locaux_commerciaux = 5,
        nb_bureaux = 25,
        autre_locaux_hors_convention = "quelques uns",
        vendeur = "identité du vendeur",
        acquereur = "identité de l'acquéreur",
        permis_construire = "123 456 789 ABC",
        date_achevement_previsible = datetime.date.today() + datetime.timedelta(days=365),
        date_achat = datetime.date.today() - datetime.timedelta(days=365),
        date_achevement = datetime.date.today() + datetime.timedelta(days=465),
    )

def assert_xlsx(self, my_class, file_name):
    filepath = f'{settings.BASE_DIR}/static/files/{file_name}.xlsx'
    with open(filepath, "rb") as excel:
        my_wb = load_workbook(filename=BytesIO(excel.read()), data_only=True)
        self.assertIn(my_class.sheet_name, my_wb)
        my_ws = my_wb[my_class.sheet_name]

        column_values = []
        for col in my_ws.iter_cols(min_col=1, max_col=my_ws.max_column, min_row=1, max_row=1):
            for cell in col:
                column_values.append(cell.value)

        for key in my_class.import_mapping:
            self.assertIn(key, column_values)
