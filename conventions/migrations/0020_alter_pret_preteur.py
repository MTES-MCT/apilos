# Generated by Django 3.2.13 on 2022-05-31 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0019_auto_20220418_1602"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pret",
            name="preteur",
            field=models.CharField(
                choices=[
                    ("ETAT", "Etat"),
                    ("EPCI", "EPCI"),
                    ("REGION", "Région"),
                    ("VILLE", "Ville"),
                    ("CDCF", "CDC pour le foncier"),
                    ("CDCL", "CDC pour le logement"),
                    ("COMMUNE", "Commune et action logement"),
                    ("ANRU", "ANRU"),
                    ("AUTRE", "Autre"),
                ],
                default="AUTRE",
                max_length=25,
            ),
        ),
    ]
