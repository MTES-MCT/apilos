# Generated by Django 3.2.13 on 2022-07-14 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0026_auto_20220712_2200"),
    ]

    operations = [
        migrations.RenameField(
            model_name="convention",
            old_name="fichier_signe",
            new_name="nom_fichier_signe",
        ),
        migrations.AddField(
            model_name="convention",
            name="televersement_convention_signee_le",
            field=models.DateTimeField(null=True),
        ),
    ]
