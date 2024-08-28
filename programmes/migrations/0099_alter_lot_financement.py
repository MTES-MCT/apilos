# Generated by Django 4.2.13 on 2024-08-19 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0098_alter_lot_financement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lot",
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
                    ("SALLS", "SALLS"),
                    ("SECD_VIE", "SECD_VIE"),
                ],
                default="PLUS",
                max_length=25,
            ),
        ),
    ]