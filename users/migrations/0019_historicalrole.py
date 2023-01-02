# Generated by Django 4.1.4 on 2023-01-02 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ("bailleurs", "0014_alter_bailleur_capital_social_and_more"),
        ("instructeurs", "0008_administration_nb_convention_exemplaires"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("users", "0018_historicaluser"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalRole",
            fields=[
                ("id", models.IntegerField(blank=True, db_index=True)),
                (
                    "typologie",
                    models.CharField(
                        choices=[
                            ("INSTRUCTEUR", "Instructeur"),
                            ("BAILLEUR", "Bailleur"),
                            ("ADMINISTRATEUR", "administrateur"),
                        ],
                        default="BAILLEUR",
                        max_length=25,
                    ),
                ),
                ("perimetre_region", models.CharField(max_length=10, null=True)),
                ("perimetre_departement", models.CharField(max_length=10, null=True)),
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
                (
                    "administration",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="instructeurs.administration",
                    ),
                ),
                (
                    "bailleur",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="bailleurs.bailleur",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="auth.group",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical role",
                "verbose_name_plural": "historical roles",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
