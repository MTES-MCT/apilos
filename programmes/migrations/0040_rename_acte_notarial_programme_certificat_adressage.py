# Generated by Django 3.2.12 on 2022-03-29 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0039_alter_programme_adresse"),
    ]

    operations = [
        migrations.RenameField(
            model_name="programme",
            old_name="acte_notarial",
            new_name="certificat_adressage",
        ),
    ]
