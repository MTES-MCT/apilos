# Generated by Django 4.2.8 on 2024-01-05 20:13

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("conventions", "0076_alter_convention_avenant_types_and_more"),
    ]

    operations = [
        TrigramExtension(),
    ]