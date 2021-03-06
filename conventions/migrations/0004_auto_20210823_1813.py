# Generated by Django 3.2.5 on 2021-08-23 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0003_auto_20210728_1536"),
    ]

    operations = [
        migrations.AddField(
            model_name="convention",
            name="comments",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="convention",
            name="financement",
            field=models.CharField(
                choices=[
                    ("PLUS", "PLUS"),
                    ("PLAI", "PLAI"),
                    ("PLAI_ADP", "PLAI_ADP"),
                    ("PLUS-PLAI", "PLUS-PLAI"),
                    ("PLS", "PLS"),
                ],
                default="PLUS",
                max_length=25,
            ),
        ),
    ]
