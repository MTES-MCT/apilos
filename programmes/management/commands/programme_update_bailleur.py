from django.core.management.base import BaseCommand
from django.db import transaction

from programmes.models import Programme
from bailleurs.models import Bailleur


class Command(BaseCommand):
    # pylint: disable=R0912,R0914,R0915
    def handle(self, *args, **options):

        programme_uuid = input("Quel est l'identifiant UUID du programme à modifier ? ")
        programme = (
            Programme.objects.prefetch_related("lot_set__logements__annexes")
            .prefetch_related("lot_set__type_stationnements")
            .prefetch_related("logementedd_set")
            .prefetch_related("conventions__pret_set")
            .prefetch_related("referencecadastrale_set")
            .get(uuid=programme_uuid)
        )
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
            with transaction.atomic():
                programme.bailleur = bailleur
                programme.save()
                programme.lot_set.all().update(bailleur=bailleur)
                programme.logementedd_set.all().update(bailleur=bailleur)
                programme.referencecadastrale_set.all().update(bailleur=bailleur)
                programme.conventions.all().update(bailleur=bailleur)
                for convention in programme.conventions.all():
                    convention.pret_set.all().update(bailleur=bailleur)
                for lot in programme.lot_set.all():
                    lot.type_stationnements.all().update(bailleur=bailleur)
                    lot.logements.all().update(bailleur=bailleur)
                    for logement in lot.logements.all():
                        logement.annexes.all().update(bailleur=bailleur)
            print(
                f"le bailleur du programme `{programme}` a été mise à jour "
                + f"avec le bailleur de siret `{bailleur_siret}`"
            )
