# Generated by Django 4.1.5 on 2023-01-09 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0061_alter_locauxcollectifs_type_local"),
    ]

    operations = [
        migrations.AlterField(
            model_name="annexe",
            name="typologie",
            field=models.CharField(
                choices=[
                    ("TERRASSE", "Terrasse"),
                    ("JARDIN", "Jardin"),
                    ("COUR", "Cour"),
                ],
                default="TERRASSE",
                max_length=25,
            ),
        ),
        migrations.RunSQL(
            "UPDATE programmes_annexe SET typologie = 'COUR'  where typologie ='CAVE' ;",
            "UPDATE programmes_annexe SET typologie = 'CAVE'  where typologie ='COUR' ;",
        ),
    ]
