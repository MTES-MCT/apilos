# Generated by Django 5.1.1 on 2024-10-10 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0113_lot_loyer_associations_foncieres"),
    ]

    operations = [
        migrations.AddField(
            model_name="logement",
            name="import_order",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]