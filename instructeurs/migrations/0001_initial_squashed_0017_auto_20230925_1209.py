# Generated by Django 4.2.11 on 2024-04-17 12:45

import uuid

import simple_history.models
from django.conf import settings
from django.db import migrations, models

# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# instructeurs.migrations.0015_administration_code_dans_galion_and_more
# instructeurs.migrations.0016_auto_20230522_1248
# instructeurs.migrations.0017_auto_20230925_1209


class Migration(migrations.Migration):

    replaces = [
        ("instructeurs", "0001_initial"),
        ("instructeurs", "0002_administration_ville_signature"),
        ("instructeurs", "0003_auto_20220107_1209"),
        ("instructeurs", "0004_auto_20220202_1444"),
        ("instructeurs", "0005_administration_prefix_convention"),
        ("instructeurs", "0006_auto_20220601_1653"),
        ("instructeurs", "0007_alter_administration_adresse"),
        ("instructeurs", "0008_administration_nb_convention_exemplaires"),
        ("instructeurs", "0009_administration_signature_label"),
        ("instructeurs", "0010_alter_administration_signature_label_extra"),
        ("instructeurs", "0011_alter_administration_adresse_and_more"),
        (
            "instructeurs",
            "0012_rename_signature_label_extra_administration_signature_bloc_signature",
        ),
        ("instructeurs", "0013_historicaladministration"),
        ("instructeurs", "0014_remove_historicaladministration_history_user_and_more"),
        ("instructeurs", "0015_administration_code_dans_galion_and_more"),
        ("instructeurs", "0016_auto_20230522_1248"),
        ("instructeurs", "0017_auto_20230925_1209"),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Administration",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("nom", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=255, unique=True)),
                ("ville_signature", models.CharField(max_length=255, null=True)),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("mis_a_jour_le", models.DateTimeField(auto_now=True)),
                (
                    "prefix_convention",
                    models.CharField(
                        default="{département}/{zone}/{mois}/{année}/80.416/",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("adresse", models.TextField(blank=True, null=True)),
                ("code_postal", models.CharField(blank=True, max_length=5, null=True)),
                ("ville", models.CharField(blank=True, max_length=255, null=True)),
                ("nb_convention_exemplaires", models.IntegerField(default=3)),
                ("signataire_bloc_signature", models.TextField(blank=True, null=True)),
                ("code_dans_galion", models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalAdministration",
            fields=[
                ("id", models.IntegerField(blank=True, db_index=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("nom", models.CharField(max_length=255)),
                ("code", models.CharField(db_index=True, max_length=255)),
                ("ville_signature", models.CharField(max_length=255, null=True)),
                ("adresse", models.TextField(blank=True, null=True)),
                ("code_postal", models.CharField(blank=True, max_length=5, null=True)),
                ("ville", models.CharField(blank=True, max_length=255, null=True)),
                ("nb_convention_exemplaires", models.IntegerField(default=3)),
                (
                    "prefix_convention",
                    models.CharField(
                        default="{département}/{zone}/{mois}/{année}/80.416/",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("signataire_bloc_signature", models.TextField(blank=True, null=True)),
                ("cree_le", models.DateTimeField(blank=True, editable=False)),
                ("mis_a_jour_le", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                ("history_user_id", models.IntegerField(null=True)),
                ("code_dans_galion", models.CharField(max_length=255, null=True)),
            ],
            options={
                "verbose_name": "historical administration",
                "verbose_name_plural": "historical administrations",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
