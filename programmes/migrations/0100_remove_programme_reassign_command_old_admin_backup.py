# Generated by Django 4.2.13 on 2024-08-22 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0099_alter_lot_financement"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="programme",
            name="reassign_command_old_admin_backup",
        ),
    ]