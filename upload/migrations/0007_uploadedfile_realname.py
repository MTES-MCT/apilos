# Generated by Django 5.1 on 2024-08-29 09:51

from django.db import migrations, models


def check_uploads_without_filename(apps, schema_editor):
    UploadedFile = apps.get_model("upload", "UploadedFile")
    _counter = UploadedFile.objects.filter(filename__isnull=True).count()
    assert _counter == 0, f"migration error, still {_counter} uploads without filename."


def fill_realname_field(apps, schema_editor):
    UploadedFile = apps.get_model("upload", "UploadedFile")
    UploadedFile.objects.update(realname=models.F("filename"))


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("upload", "0001_initial_squashed_0006_auto_20220107_1209"),
    ]

    operations = [
        migrations.AddField(
            model_name="uploadedfile",
            name="realname",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunPython(
            code=check_uploads_without_filename,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            code=fill_realname_field,
            reverse_code=migrations.RunPython.noop,
            atomic=True,
        ),
    ]
