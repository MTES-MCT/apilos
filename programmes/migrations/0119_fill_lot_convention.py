import logging
import uuid

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import migrations
from django.db.models import Count, F, IntegerField, OuterRef, Subquery

from conventions.models.choices import ConventionStatut


def fill_lot_convention(apps, schema_editor):
    Convention = apps.get_model("conventions", "Convention")
    Lot = apps.get_model("programmes", "Lot")

    # Suppression des lots sans convention
    lots_without_conventions = Lot.objects.annotate(
        convention_count=Count("conventions")
    ).filter(convention_count=0)

    for lot in lots_without_conventions:
        lot.delete()

    # Pour chaque lot qui a plusieurs conventions, on souhaite copier le lot
    # pour que chaque convention ait son propre lot

    # Trouver tous les lots qui ont plusieurs conventions
    lots_multi_conventions = Lot.objects.annotate(
        convention_count=Count("conventions")
    ).filter(convention_count__gt=1)
    logging.warning(f"{lots_multi_conventions.count()} lots with multiple conventions.")

    # Pour chaque lot, on crée un nouveau lot pour chaque convention
    for lot in lots_multi_conventions:
        for convention in lot.conventions.all()[1:]:
            lot.pk = None
            lot.uuid = uuid.uuid4()
            lot.save()
            convention.lot = lot
            convention.save()

    count_lot = Lot.objects.count()
    count_conventions = Convention.objects.count()
    if count_lot != count_conventions:
        logging.warning(f" >> {count_lot} lots and {count_conventions} conventions.")
        raise Exception("Not implemented yet.")

    try:
        Convention._meta.get_field("lot")
    except FieldDoesNotExist:
        pass
    else:
        queryset = Lot.objects.exclude(convention__isnull=False).annotate(
            mirrored_convention_id=Subquery(
                Convention.objects.exclude(statut=ConventionStatut.ANNULEE)
                .filter(lot_id=OuterRef("pk"))
                .values("pk")[:1],
                output_field=IntegerField(),
            )
        )

        queryset.update(convention_id=F("mirrored_convention_id"))

    _count_null = Lot.objects.filter(convention__isnull=True).count()
    assert (
        _count_null == 0
    ), f"migration error, still {_count_null} lots without any convention linked."


def undo_fill_lot_convention(apps, schema_editor):
    Lot = apps.get_model("programmes", "Lot")
    Lot.objects.update(convention=None)


class Migration(migrations.Migration):
    dependencies = [
        ("programmes", "0118_lot_convention"),
    ]
    operations = []

    if settings.ENVIRONMENT != "test":
        operations.extend(
            [
                migrations.RunSQL(
                    # copy de la table programmes_lot pour la sauvegarde
                    "CREATE TABLE programmes_lot_backup AS "
                    "SELECT * FROM programmes_lot;",
                    "DROP TABLE programmes_lot_backup;",
                ),
                migrations.RunPython(
                    fill_lot_convention,
                    undo_fill_lot_convention,
                ),
            ]
        )
