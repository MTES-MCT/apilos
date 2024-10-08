# Generated by Django 4.2.11 on 2024-04-24 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "programmes",
            "0001_initial_squashed_0091_programme_reassign_command_old_admin_backup",
        ),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="programme",
            name="programme_numero_galion_idx",
        ),
        migrations.RenameField(
            model_name="programme",
            old_name="numero_galion",
            new_name="numero_operation",
        ),
        migrations.AddIndex(
            model_name="programme",
            index=models.Index(
                fields=["numero_operation"], name="programme_numero_operation_idx"
            ),
        ),
    ]
