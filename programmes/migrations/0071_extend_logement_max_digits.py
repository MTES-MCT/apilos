# Generated by Django 4.1.7 on 2023-03-02 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0070_create_model_indiceevolutionloyer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="logement",
            name="surface_annexes",
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
    ]
