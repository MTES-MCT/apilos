from django.core.management.base import BaseCommand
from django.db import transaction

from bailleurs.models import Bailleur
from programmes.models import Programme


class Command(BaseCommand):
    def handle(self, *args, **options):

        programme_uuid = input("Quel est l'identifiant UUID du programme à modifier ? ")
        programme = (
            Programme.objects
            # .prefetch_related("lots__logements__annexes")
            # .prefetch_related("lots__type_stationnements")
            .prefetch_related("logementedds")
            .prefetch_related("conventions__prets")
            .prefetch_related("referencecadastrales")
            .get(uuid=programme_uuid)
        )
        self.stdout.write(
            f"le programme `{programme_uuid}` : `{programme}` va être modifié"
        )

        bailleur_siret = input(
            "Quel est le siret du bailleur auquel le programme doit etre rattacher ? "
        )
        bailleur = Bailleur.objects.get(siret=bailleur_siret)
        self.stdout.write(
            f"le programme `{programme}` va être attribué au bailleur `{bailleur}` "
            + f"de siret `{bailleur_siret}`"
        )

        go = input("Modifier le bailleur du programme (Non/oui)?")

        if go.lower() == "oui":
            with transaction.atomic():
                programme.bailleur = bailleur
                programme.save()
            self.stdout.write(
                f"le bailleur du programme `{programme}` a été mise à jour "
                + f"avec le bailleur de siret `{bailleur_siret}`"
            )
