# Generated by Django 5.1.3 on 2025-01-24 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0100_auto_20241213_1554"),
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
                    ("PLAI_FTM", "PLAI Foyer de travailleurs migrants"),
                    ("PLAI_RE", "PLAI Réhabiliation"),
                    ("PLUS-PLAI", "PLUS-PLAI"),
                    ("PLS", "PLS"),
                    ("PSH", "PSH"),
                    ("PALULOS", "PALULOS"),
                    ("PALU_AV_21", "PALULOS avant 2021"),
                    ("PALUCOM", "PALULOS communal"),
                    ("PALU_COM", "PALULOS communal"),
                    ("PALU_RE", "PALULOS Réhabiliation"),
                    ("SANS_FINANCEMENT", "Sans Financement"),
                    ("LLS", "LLS"),
                    ("LLTS", "LLTS"),
                    ("LLTSA", "LLTSA"),
                    ("PLS_DOM", "PLS outre-mer"),
                    ("SALLS_R", "SALLS Réhabiliation"),
                    ("SALLS_P", "SALLS Parasismique"),
                    ("SECD_VIE", "Seconde vie"),
                    ("RENO", "Renovation"),
                ],
                default="PLUS",
                max_length=25,
            ),
        ),
    ]
