# Generated by Django 5.1.3 on 2025-01-31 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0101_alter_convention_financement"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="convention",
            name="financement",
        ),
    ]
