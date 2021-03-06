# Generated by Django 3.2.13 on 2022-05-30 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0044_auto_20220511_1629"),
    ]

    operations = [
        migrations.AlterField(
            model_name="typestationnement",
            name="typologie",
            field=models.CharField(
                choices=[
                    ("GARAGE_AERIEN", "Garage aérien"),
                    ("GARAGE_ENTERRE", "Garage enterré"),
                    ("PLACE_STATIONNEMENT", "Place de stationnement"),
                    ("PARKING_EXTERIEUR_PRIVATIF", "Parking extérieur privatif"),
                    ("PARKING_SOUSSOL", "Parking en sous-sol ou en superstructure"),
                    ("GARAGE_BOXE_SIMPLE", "Garage boxé simple"),
                    ("GARAGE_BOXE_DOUBLE", "Garage boxé double"),
                    ("EXTERIEUR_BOXE", "extérieur boxé"),
                    ("SOUSSOL_BOXE", "en sous-sol boxé"),
                    ("CARPORT", "Carport"),
                    ("DEUX_ROUES_EXTERIEUR", "2 roues en extérieur"),
                    ("DEUX_ROUES_SOUSSOL", "2 roues en sous-sol"),
                ],
                default="PLACE_STATIONNEMENT",
                max_length=35,
            ),
        ),
    ]
