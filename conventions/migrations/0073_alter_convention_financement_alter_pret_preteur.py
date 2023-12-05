# Generated by Django 4.2.5 on 2023-11-27 21:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "conventions",
            "0072_alter_convention_televersement_convention_signee_le_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="convention",
            name="financement",
            field=models.CharField(
                choices=[
                    ("PLUS", "PLUS"),
                    ("PLUS_CD", "PLUS_CD"),
                    ("PLAI", "PLAI"),
                    ("PLAI_ADP", "PLAI_ADP"),
                    ("PLUS-PLAI", "PLUS-PLAI"),
                    ("PLS", "PLS"),
                    ("PSH", "PSH"),
                    ("PALULOS", "PALULOS"),
                    ("SANS_FINANCEMENT", "Sans Financement"),
                ],
                default="PLUS",
                max_length=25,
            ),
        ),
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
                    ("AUTRE", "Autre/Subventions"),
                ],
                default="AUTRE",
                max_length=25,
            ),
        ),
    ]