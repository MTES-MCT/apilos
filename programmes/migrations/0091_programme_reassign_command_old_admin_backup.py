# Generated by Django 4.2.9 on 2024-02-26 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("programmes", "0090_programme_search_vector_update"),
    ]

    operations = [
        migrations.AddField(
            model_name="programme",
            name="reassign_command_old_admin_backup",
            field=models.JSONField(default=None, null=True),
        ),
    ]
