# Generated by Django 4.2.7 on 2023-12-18 10:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("programmes", "0083_alter_logementedd_financement_alter_lot_financement"),
    ]

    operations = [
        migrations.AddField(
            model_name="programme",
            name="edd_stationnements",
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
    ]