# Generated by Django 3.2.5 on 2021-07-26 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0002_auto_20210706_1816"),
    ]

    operations = [
        migrations.AddField(
            model_name="programme",
            name="annee_gestion_programmation",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="programme",
            name="numero_gallion",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="programme",
            name="surface_utile_totale",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="programme",
            name="type_habitat",
            field=models.CharField(
                choices=[("INDIVIDUEL", "Individuel"), ("COLLECTIF", "Collectif")],
                default="INDIVIDUEL",
                max_length=25,
            ),
        ),
        migrations.AddField(
            model_name="programme",
            name="zone_123",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="programme",
            name="zone_abc",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
