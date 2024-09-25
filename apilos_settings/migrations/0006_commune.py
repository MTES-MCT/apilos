# Generated by Django 4.2.13 on 2024-08-29 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apilos_settings", "0005_alter_departement_code_insee_region"),
    ]

    operations = [
        migrations.CreateModel(
            name="Commune",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code_postal", models.CharField(blank=True, max_length=5)),
                ("commune", models.CharField(blank=True, max_length=255)),
            ],
            options={
                "managed": False,
            },
        ),
    ]