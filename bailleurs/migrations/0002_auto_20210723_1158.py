# Generated by Django 3.2.5 on 2021-07-23 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bailleurs", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bailleur",
            name="siege",
        ),
        migrations.AddField(
            model_name="bailleur",
            name="adresse",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="bailleur",
            name="code_postal",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="bailleur",
            name="ville",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="bailleur",
            name="capital_social",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="bailleur",
            name="dg_date_deliberation",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="bailleur",
            name="dg_fonction",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="bailleur",
            name="dg_nom",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="bailleur",
            name="operation_exceptionnelle",
            field=models.TextField(null=True),
        ),
    ]
