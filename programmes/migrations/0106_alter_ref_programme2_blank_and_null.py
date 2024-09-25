# Generated by Django 4.2.13 on 2024-09-03 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("instructeurs", "0001_initial_squashed_0017_auto_20230925_1209"),
        ("programmes", "0105_alter_ref_programme1_blank_and_null"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programme",
            name="annee_gestion_programmation",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="autres_locaux_hors_convention",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="certificat_adressage",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="code_insee_commune",
            field=models.CharField(blank=True, default="", max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="code_insee_departement",
            field=models.CharField(blank=True, default="", max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="code_insee_region",
            field=models.CharField(blank=True, default="", max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="code_postal",
            field=models.CharField(blank=True, default="", max_length=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_achat",
            field=models.DateField(blank=True, null=True),
        ),
    ]