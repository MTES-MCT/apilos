# Generated by Django 3.2.9 on 2021-12-01 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bailleurs", "0004_alter_bailleur_capital_social"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bailleur",
            old_name="dg_date_deliberation",
            new_name="signataire_date_deliberation",
        ),
        migrations.RenameField(
            model_name="bailleur",
            old_name="dg_fonction",
            new_name="signataire_fonction",
        ),
        migrations.RenameField(
            model_name="bailleur",
            old_name="dg_nom",
            new_name="signataire_nom",
        ),
    ]
