# Generated by Django 4.2.13 on 2024-09-30 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0111_historicalprogramme"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="programme",
            index=models.Index(
                fields=["code_insee_region"], name="prog_code_insee_reg_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="programme",
            index=models.Index(
                fields=["code_insee_departement"], name="prog_code_insee_dept_idx"
            ),
        ),
    ]
