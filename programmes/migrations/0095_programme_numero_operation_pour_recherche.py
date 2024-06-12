# Generated by Django 4.2.13 on 2024-06-03 15:06

from django.db import migrations, models


def set_numero_op_for_search(apps, schema_editor):
    Programme = apps.get_model("programmes", "Programme")
    for p in Programme.objects.exclude(numero_operation__isnull=True).exclude(
        numero_operation=""
    ):
        p.numero_operation_pour_recherche = (
            p.numero_operation.replace("/", "")
            .replace("-", "")
            .replace(" ", "")
            .replace(".", "")
        )
        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0094_alter_lot_financement_alter_programme_zone_abc"),
    ]

    operations = [
        migrations.AddField(
            model_name="programme",
            name="numero_operation_pour_recherche",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddIndex(
            model_name="programme",
            index=models.Index(
                fields=["numero_operation_pour_recherche"],
                name="programme_num_for_search_idx",
            ),
        ),
        migrations.RunPython(set_numero_op_for_search, migrations.RunPython.noop),
    ]