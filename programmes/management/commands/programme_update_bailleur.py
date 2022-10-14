from django.core.management.base import BaseCommand

from programmes.models import Programme
from programmes.services import programme_change_bailleur
from bailleurs.models import Bailleur


class Command(BaseCommand):
    # pylint: disable=R0912,R0914,R0915
    def handle(self, *args, **options):

        programme_uuid = input("Quel est l'identifiant UUID du programme à modifier ? ")
        programme = Programme.objects.get(uuid=programme_uuid)
        print(f"le programme `{programme_uuid}` : `{programme}` va être modifié")

        bailleur_siret = input(
            "Quel est le siret du bailleur auquel le programme doit etre rattacher ? "
        )
        bailleur = Bailleur.objects.get(siret=bailleur_siret)
        print(
            f"le programme `{programme}` va être attribué au bailleur `{bailleur}` "
            + f"de siret `{bailleur_siret}`"
        )

        go = input("Modifier le bailleur du programme (Non/oui)?")

        if go.lower() == "oui":
            programme_change_bailleur(programme, bailleur)
            print(
                f"le bailleur du programme `{programme}` a été mise à jour "
                + f"avec le bailleur de siret `{bailleur_siret}`"
            )
