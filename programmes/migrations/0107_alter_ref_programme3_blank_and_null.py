# Generated by Django 4.2.13 on 2024-09-03 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("instructeurs", "0001_initial_squashed_0017_auto_20230925_1209"),
        ("programmes", "0106_alter_ref_programme2_blank_and_null"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programme",
            name="date_achevement",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_achevement_compile",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_achevement_previsible",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_acte_notarie",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_autorisation_hors_habitat_inclusif",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_convention_location",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="date_residence_argement_gestionnaire_intermediation",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="departement_residence_argement_gestionnaire_intermediation",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
    ]