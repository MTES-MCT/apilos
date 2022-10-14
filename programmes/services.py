from django.db import transaction
from django.db.models.query import prefetch_related_objects

from conventions.models import ConventionStatut


def programme_change_bailleur(programme, bailleur):
    prefetch_related_objects(
        [programme],
        [
            "lot_set__logements__annexes",
            "lot_set__type_stationnements",
            "logementedd_set",
            "conventions__pret_set",
            "referencecadastrale_set",
        ],
    )
    for convention in programme.conventions:
        if convention.statut in [ConventionStatut.A_SIGNER, ConventionStatut.SIGNEE]:
            raise Exception(
                "It is not possible to update bailleur of the programme"
                + " because some convention are validated"
            )

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
