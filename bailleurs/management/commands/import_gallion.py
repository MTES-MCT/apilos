import os
from pathlib import Path

from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string
from instructeurs.models import Administration
from bailleurs.models import Bailleur
from programmes.models import Programme, Financement, Lot

def str_row(row):
  return (f"Bailleur (siret, nom) : {row['MOA (code SIRET)']} - {row['MOA (nom officiel)']}" +
    f", Administration (code, nom) : {row['Gestionnaire (code)']} - {row['Gestionnaire']}" +
    f", Programme (nom, ville) : {row['Nom Opération']} - {row['Commune']},"+
    f" Financement : {row['Produit']}")


class Command(BaseCommand):
  def handle(self, **options):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = os.path.join(BASE_DIR, "documents", "v3.xlsx")



    file_path_input = input("Enter your value (default: "+file_path+"): ")
    file_path = file_path_input or file_path
    wb = load_workbook(file_path)
    if not wb.sheetnames:
      print('Error, the worksheet is not compatible, no sheet detected')
      exit(1)

    sheet_name = 'Rapport 1'
    sheet_name_input = input("Enter the sheetname to read (default: "+sheet_name+"): ")
    sheet_name = sheet_name_input or sheet_name
    ws = wb[sheet_name]

    # Create one object by row
    column_from_index = {}
    for tuple in ws['B4':'AH4']:
      for cell in tuple:
        column_from_index[cell.column] = str(cell.value).strip()
#        print(cell.value)

    # List here the fields to strip
    to_sprit = [
      'Nom Opération',
      'N° Opération GALION',
      'Commune',
      'Zone ABC',
      'Gestionnaire',
      'Gestionnaire (code)',
      'MOA (nom officiel)',
      'MOA (code SIRET)',
      'MOA Adresse 1',
      'MOA Code postal',
      'MOA Ville',
      "Type d'habitat",
      'Nom Opération',
      'Adresse Opération 1',
      'Opération code postal',
      'Nature logement',
      'Type Bénéficiaire',
      'Produit',
    ]

    to_sprit_input = map(lambda x: x.strip(), input("List here the fields to strip (default: " + ','.join(to_sprit) + "): ").split(','))
    to_sprit = to_sprit_input or to_sprit

    my_objects = []
    count_rows = 0
    count_inserted = 0
    for row in ws.iter_rows(min_row=5,max_row=ws.max_row,min_col=2, max_col=ws.max_column):
      count_rows += 1
      my_row = {}
      for cell in row:
        my_row[column_from_index[cell.column]] = str(cell.value).strip() if cell.column in to_sprit else cell.value
      if len(my_row['MOA (code SIRET)']) != 14:
        print(f"le siret n'a pas de bon format, l'entrée est ignorée: {str_row(my_row)}")
        continue
      if len(my_row['Gestionnaire (code)']) != 5:
        print(f"le service instructeur n'est pas renseigné, l'entrée est ignorée: {str_row(my_row)}")
        continue
      if not my_row['Produit'] in dir(Financement):
        if my_row['Produit'][0:4] in ['PLUS','PLAI']:
          my_row['Produit'] = my_row['Produit'][0:4]
        else:
          print(f"le financement n'est pas supporté, l'entrée est ignorée: {str_row(my_row)}")
          continue
      my_objects.append(my_row)
      count_inserted += 1
    print(f"{count_rows - count_inserted} / {count_rows} lignes ignorées")

    Administration.map_and_create(my_objects)
    Bailleur.map_and_create(my_objects)
    Programme.map_and_create(my_objects)
    Lot.map_and_create(my_objects)



# Année Gestion Programmation
# Département
# N° Opération GALION
# Commune
# Zone 123
# Zone ABC
# Gestionnaire
# Gestionnaire (code)
# Gestionnaire (code SIREN)
# MOA (nom officiel)
# MOA (code SIRET)
# MOA Adresse 1
# MOA Code postal
# MOA Ville
# Type d'habitat
# Nom Opération
# Adresse Opération 1
# Opération code postal
# Année Achèvement Travaux
# Nature logement
# Type Bénéficiaire
# Produit
# Nb logts
# SU totale
# Nb Garages aériens
# Loyer Garages aériens
# Nb Garages enterrés
# Loyer Garages enterrés
# Nb Places Stationnement
# Loyer Places Stationnement
