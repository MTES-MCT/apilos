# Generated by Django 4.2.9 on 2024-01-29 19:53

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bailleurs", "0023_alter_bailleur_siren_alter_bailleur_uuid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bailleur",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="historicalbailleur",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="bailleur",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="search_vector_bailleur_idx"
            ),
        ),
    ]