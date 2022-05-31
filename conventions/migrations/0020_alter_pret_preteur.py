# Generated by Django 3.2.13 on 2022-05-30 20:54

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
                    ("ETAT", "Subvention Etat"),
                    ("EPCI", "EPCI"),
                    ("REGION", "Subvention Région"),
                    ("VILLE", "Subvention Ville"),
                    ("CDCF", "CDC pour le foncier"),
                    ("CDCL", "CDC pour le logement"),
                    ("COMMUNE", "Subvention Action Logement"),
                    ("ANRU", "ANRU"),
                    ("AUTRE", "Autre (prêt ou subvention)"),
                ],
                default="AUTRE",
                max_length=25,
            ),
        ),
    ]
