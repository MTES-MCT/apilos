# Generated by Django 5.1.5 on 2025-04-02 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0025_remove_historicaluser_administrateur_de_compte_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaluser",
            name="secondary_email",
            field=models.EmailField(blank=True, max_length=264),
        ),
        migrations.AddField(
            model_name="user",
            name="secondary_email",
            field=models.EmailField(blank=True, max_length=264),
        ),
    ]
