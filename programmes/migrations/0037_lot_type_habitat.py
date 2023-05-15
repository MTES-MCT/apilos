# Generated by Django 3.2.12 on 2022-02-22 07:48

from django.db import migrations, models


def copy_type_habitat_to_lot(apps, schema_editor):
    Lot = apps.get_model("programmes", "Lot")

    for lot in Lot.objects.all():
        programme = lot.programme
        lot.type_habitat = programme.type_habitat
        lot.save()


class Migration(migrations.Migration):
    dependencies = [
        ("programmes", "0036_auto_20220215_1757"),
    ]

    operations = [
        migrations.AddField(
            model_name="lot",
            name="type_habitat",
            field=models.CharField(
                choices=[
                    ("MIXTE", "Mixte"),
                    ("INDIVIDUEL", "Individuel"),
                    ("COLLECTIF", "Collectif"),
                ],
                default="INDIVIDUEL",
                max_length=25,
            ),
        ),
        migrations.RunPython(copy_type_habitat_to_lot, migrations.RunPython.noop),
    ]
