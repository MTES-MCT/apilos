# Generated by Django 3.2.12 on 2022-03-17 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apilos_settings", "0002_auto_20220317_1211"),
        ("users", "0007_user_preferences_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="filtre_departements",
            field=models.ManyToManyField(to="apilos_settings.Departement"),
        ),
    ]
