# Generated by Django 4.1.4 on 2022-12-15 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0045_convention_gestionnaire_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="convention",
            name="attribution_agees_autonomie",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_agees_autre",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_agees_autre_detail",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_agees_desorientees",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_agees_ephad",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_agees_petite_unite",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_handicapes_autre",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_handicapes_autre_detail",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_handicapes_foyer",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_handicapes_foyer_de_vie",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_handicapes_foyer_medicalise",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_inclusif_activites",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_inclusif_conditions_admission",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_inclusif_conditions_specifiques",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_inclusif_modalites_attribution",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_inclusif_partenariats",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_modalites_choix_personnes",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_modalites_reservations",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_prestations_facultatives",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_prestations_integrees",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name="convention",
            name="attribution_reservation_prefectoral",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
