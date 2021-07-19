import os
from pathlib import Path

from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string

class Command(BaseCommand):
  def handle(self, **options):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = os.path.join(BASE_DIR, "documents", "export_sisal.xlsx")
    val = input("Enter your value ("+file_path+"): ")
    if not(val):
      val = file_path
    wb = load_workbook(val)

    sheet_name = 'Rapport 1'
    ws = wb[sheet_name]
    first_cell_of_table = 'B4'

    # Create one object by row
    column_from_index = {}
    for tuple in ws['B4':'AH4']:
      for cell in tuple:
        column_from_index[cell.column] = cell.value
        print(cell.value)

    my_objects = []
    for row in ws.iter_rows(min_row=5,max_row=ws.max_row,min_col=2, max_col=ws.max_column): #(    'B{}:AH{}'.format(4,int(ws.max_row))):
      my_row = {}
      for cell in row:
        my_row[column_from_index[cell.column]] = cell.value
      my_objects.append(my_row)

    print(my_objects)

    # Close the workbook after reading
    wb.close()




# bailleur = {
#   'MOA (nom officiel)' : bailleur.nom,
#   'MOA (code SIRET)' : bailleur.siret,
#   'MOA Adresse 1' : bailleur.siege ?
#   'MOA Code postal' : bailleur.siege ?
#   'MOA Ville' : bailleur.siege ?
#   '' : bailleur.capital_social
#   '' : bailleur.dg_nom
#   '' : bailleur.dg_fonction
#   '' : bailleur.dg_date_deliberation
# }

# Programme = {
#   'Nom Opération': programme.nom,
#   ? : programme.code_postal,
#   'Commune': programme.ville,
#   'Adresse Opération 1': programme.adresse,
#   'Nb logts': programme.nb_logements,
#   'Zone 123': ?
#   'Zone ABC': ?
#   'Type Financement' : ? #beaucoup de mixte
#   'Produit' : ? # PLUS / PLAI/ PLS ... t plus encore
#   'Nature logement' ? # ordinaire, résidences, pension... etc
#   'Réf. Coordonnées XY': ?
#   'Type Bénéficiaire': ?, # Ménage Étidiants Jeunes...
#   'SU totale' : ?,
#   'Nb Jardins' : ?
#   'Loyer Jardins' : ?
#   ? : programme.type_operation,
#   ? : programme.anru,
#   ? : programme.nb_logement_non_conventionne,
#   ? : programme.nb_locaux_commerciaux,
#   ? : programme.nb_bureaux,
#   ? : programme.vendeur,
#   ? : programme.acquereur,
#   ? : programme.date_acte_notarie,
#   ? : programme.reference_notaire,
#   ? : programme.reference_publication_acte,
#   ? : programme.permis_construire,
#   'Année Gestion Programmation': programme.date_achevement_previsible, #différence année et date
#   ? : programme.date_achat,
#   'Année Achèvement Travaux': programme.date_achevement, #différence année et date -> célulle toujours vide
#   'Année Gestion Début': ?,
#   'Année Gestion Clôture': ?,
#   'N° Opération GALION': ?,
#   "Type d'habitat": ?, # individuel ou collectif
#   'Gestionnaire : ?': ? # lien avec l'instance instructeur ?
# }

# ReferenceCadastrale = {
#   'Réf. Parcelle cadastrale': ?
# }

# TypeStationnement = {
#   'Nb Garages aériens' : programme.Lot.TypeStationnement.topologie/nb_stationnements, # ici je n'ai pas de notion de lot
#   'Loyer Garages aériens' : programme.Lot.TypeStationnement.topologie/loyer, # ici je n'ai pas de notion de lot
#   'Nb Garages enterrés' : programme.Lot.TypeStationnement.topologie/nb_stationnements, # ici je n'ai pas de notion de lot
#   'Loyer Garages enterrés' : programme.Lot.TypeStationnement.topologie/loyer, # ici je n'ai pas de notion de lot
#   'Nb Places Stationnement' : programme.Lot.TypeStationnement.topologie/nb_stationnements, # ici je n'ai pas de notion de lot
#   'Loyer Places Stationnement' : programme.Lot.TypeStationnement.topologie/loyer, # ici je n'ai pas de notion de lot
# }