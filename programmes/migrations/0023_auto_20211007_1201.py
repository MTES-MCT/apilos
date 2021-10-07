# Generated by Django 3.2.7 on 2021-10-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0022_auto_20211005_0921"),
    ]

    operations = [
        migrations.AlterField(
            model_name="annexe",
            name="loyer",
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name="annexe",
            name="loyer_par_metre_carre",
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name="annexe",
            name="surface_hors_surface_retenue",
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name="logement",
            name="coeficient",
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="logement",
            name="loyer",
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="logement",
            name="loyer_par_metre_carre",
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="logement",
            name="surface_annexes",
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="logement",
            name="surface_annexes_retenue",
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="logement",
            name="surface_habitable",
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="logement",
            name="surface_utile",
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="programme",
            name="surface_utile_totale",
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name="typestationnement",
            name="loyer",
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
