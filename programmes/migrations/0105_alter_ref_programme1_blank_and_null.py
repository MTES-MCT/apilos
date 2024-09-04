# Generated by Django 4.2.13 on 2024-09-03 20:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("instructeurs", "0001_initial_squashed_0017_auto_20230925_1209"),
        ("programmes", "0104_alter_ref_cadastrale_blank_and_null"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programme",
            name="acquereur",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="acte_de_propriete",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="administration",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="instructeurs.administration",
            ),
        ),
        migrations.AlterField(
            model_name="programme",
            name="adresse",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]
