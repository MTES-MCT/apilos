# Generated by Django 4.1.7 on 2023-03-16 16:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0073_lot_surface_locaux_collectifs_residentiels"),
    ]

    operations = [
        migrations.AddField(
            model_name="programme",
            name="surface_corrigee_totale",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="surface_utile_totale",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.CreateModel(
            name="RepartitionSurface",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "typologie",
                    models.CharField(
                        choices=[
                            ("T1", "T1"),
                            ("T1bis", "T1 bis"),
                            ("T1prime", "T1'"),
                            ("T2", "T2"),
                            ("T3", "T3"),
                            ("T4", "T4"),
                            ("T5", "T5"),
                            ("T6", "T6"),
                            ("T7", "T7"),
                        ],
                        default="T1",
                        max_length=25,
                    ),
                ),
                (
                    "type_habitat",
                    models.CharField(
                        choices=[
                            ("INDIVIDUEL", "Individuel"),
                            ("COLLECTIF", "Collectif"),
                        ],
                        default="INDIVIDUEL",
                        max_length=25,
                    ),
                ),
                ("quantite", models.IntegerField()),
                (
                    "lot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="surfaces",
                        to="programmes.lot",
                    ),
                ),
            ],
            options={
                "unique_together": {("lot", "typologie", "type_habitat")},
            },
        ),
    ]
