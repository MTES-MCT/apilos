# Generated by Django 4.1.7 on 2023-03-18 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "programmes",
            "0072_alter_programme_mention_publication_edd_classique_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="lot",
            name="surface_locaux_collectifs_residentiels",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
                verbose_name="Surface des locaux collectifs résidentiels",
            ),
        ),
    ]
