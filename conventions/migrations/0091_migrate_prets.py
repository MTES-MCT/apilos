# Generated by Django 4.2.13 on 2024-07-03 14:02

from django.db import migrations
from django.db.models import OuterRef, Subquery


def attach_prets_to_lot(apps, schema_editor):
    Pret = apps.get_model("conventions", "Pret")
    Convention = apps.get_model("conventions", "Convention")

    Pret.objects.update(
        lot_id=Subquery(
            Convention.objects.filter(pk=OuterRef("convention_id")).values("lot_id")[:1]
        )
    )

    _count_null = Pret.objects.filter(lot__isnull=True).count()
    assert _count_null == 0, f"migration error, still {_count_null} prets without lot."


class Migration(migrations.Migration):
    dependencies = [
        ("conventions", "0090_pret_lot"),
    ]

    operations = [
        migrations.RunPython(
            # attach_prets_to_lot,
            migrations.RunPython.noop,
            migrations.RunPython.noop,
        ),
    ]
