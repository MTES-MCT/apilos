from django.db import migrations
from django.db.models import F, IntegerField, OuterRef, Subquery


def fill_lot_convention(apps, schema_editor):
    Convention = apps.get_model("conventions", "Convention")
    Lot = apps.get_model("programmes", "Lot")

    queryset = Lot.objects.exclude(convention__isnull=False).annotate(
        mirrored_convention_id=Subquery(
            Convention.objects.filter(lot_id=OuterRef("pk")).values("pk")[:1],
            output_field=IntegerField(),
        )
    )
    print(f" >> {queryset.count()} lots to update.")  # noqa: T201

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
        ("programmes", "0116_lot_convention"),
    ]
    operations = [
        migrations.RunPython(
            fill_lot_convention,
            undo_fill_lot_convention,
        )
    ]
