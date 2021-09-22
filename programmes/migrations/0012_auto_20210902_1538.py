# Generated by Django 3.2.5 on 2021-09-02 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0011_auto_20210830_0947"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programme",
            name="type_habitat",
            field=models.CharField(
                choices=[
                    ("SANSOBJECT", "Sans Object"),
                    ("INDIVIDUEL", "Individuel"),
                    ("COLLECTIF", "Collectif"),
                ],
                default="INDIVIDUEL",
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="programme",
            name="type_operation",
            field=models.CharField(
                choices=[
                    ("SANSOBJECT", "Sans Object"),
                    ("NEUF", "Construction Neuve"),
                    ("ACQUIS", "Acquisition-Amélioration"),
                    ("DEMEMBREMENT", "Démembrement"),
                    ("REHABILITATION", "Réhabilitation"),
                    ("SANSTRAVAUX", "Sans travaux"),
                    ("USUFRUIT", "Usufruit"),
                    ("VEFA", "VEFA"),
                ],
                default="NEUF",
                max_length=25,
            ),
        ),
    ]
