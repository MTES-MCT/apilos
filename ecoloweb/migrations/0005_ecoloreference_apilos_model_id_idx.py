# Generated by Django 4.2.1 on 2023-05-26 10:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecoloweb", "0004_purge_duplicate_bailleurs"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="ecoloreference",
            index=models.Index(
                fields=["apilos_model", "apilos_id"], name="apilos_model_id_idx"
            ),
        ),
    ]
