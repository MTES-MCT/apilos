# Generated by Django 5.1.1 on 2024-11-07 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0094_convention_convention_cree_le_idx"),
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
                    ("LLS", "LLS"),
                    ("LLTS", "LLTS"),
                    ("LLTSA", "LLTSA"),
                    ("PLS_DOM", "PLS_DOM"),
                    ("SALLS_R", "SALLS Réhabiliation"),
                    ("SECD_VIE", "SECD_VIE"),
                ],
                default="PLUS",
                max_length=25,
            ),
        ),
    ]
