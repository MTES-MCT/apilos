# Generated by Django 3.2.13 on 2022-07-12 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conventions", "0025_auto_20220708_0254"),
    ]

    operations = [
        migrations.AlterField(
            model_name="convention",
            name="statut",
            field=models.CharField(
                choices=[
                    ("1. Projet", "Création d'un projet de convention"),
                    (
                        "2. Instruction requise",
                        "Projet de convention soumis à l'instruction",
                    ),
                    (
                        "3. Corrections requises",
                        "Projet de convention à modifier par le bailleur",
                    ),
                    ("4. A signer", "Convention à signer"),
                    ("5. Transmise", "Convention transmise"),
                    ("6. Résiliée", "Convention résiliée"),
                ],
                default="1. Projet",
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="conventionhistory",
            name="statut_convention",
            field=models.CharField(
                choices=[
                    ("1. Projet", "Création d'un projet de convention"),
                    (
                        "2. Instruction requise",
                        "Projet de convention soumis à l'instruction",
                    ),
                    (
                        "3. Corrections requises",
                        "Projet de convention à modifier par le bailleur",
                    ),
                    ("4. A signer", "Convention à signer"),
                    ("5. Transmise", "Convention transmise"),
                    ("6. Résiliée", "Convention résiliée"),
                ],
                default="1. Projet",
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="conventionhistory",
            name="statut_convention_precedent",
            field=models.CharField(
                choices=[
                    ("1. Projet", "Création d'un projet de convention"),
                    (
                        "2. Instruction requise",
                        "Projet de convention soumis à l'instruction",
                    ),
                    (
                        "3. Corrections requises",
                        "Projet de convention à modifier par le bailleur",
                    ),
                    ("4. A signer", "Convention à signer"),
                    ("5. Transmise", "Convention transmise"),
                    ("6. Résiliée", "Convention résiliée"),
                ],
                default="1. Projet",
                max_length=25,
            ),
        ),
    ]
