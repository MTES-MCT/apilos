# Generated by Django 4.1.5 on 2023-01-12 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instructeurs", "0009_administration_signature_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="administration",
            name="signature_label_extra",
            field=models.TextField(blank=True, null=True),
        ),
    ]
