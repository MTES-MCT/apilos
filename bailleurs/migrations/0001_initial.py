# Generated by Django 3.2.5 on 2021-07-06 14:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bailleur',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('nom', models.CharField(max_length=255)),
                ('siret', models.CharField(max_length=14)),
                ('capital_social', models.CharField(max_length=255)),
                ('siege', models.CharField(max_length=255)),
                ('dg_nom', models.CharField(max_length=255)),
                ('dg_fonction', models.CharField(max_length=255)),
                ('dg_date_deliberation', models.DateField()),
                ('operation_exceptionnelle', models.TextField()),
                ('cree_le', models.DateTimeField(auto_now_add=True)),
                ('mis_a_jour_le', models.DateTimeField(auto_now=True)),
            ],
            options={
                'permissions': (('can_edit_bailleur', 'Créer ou mettre à jour un bailleur'),),
            },
        ),
    ]
