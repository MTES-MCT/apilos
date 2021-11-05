import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("conventions", "0012_alter_pret_montant"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("nom_objet", models.CharField(max_length=255)),
                ("champ_objet", models.CharField(max_length=255)),
                ("uuid_objet", models.UUIDField()),
                ("message", models.TextField(null=True)),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("OUVERT", "Ouvert"),
                            ("RESOLU", "Résolu"),
                            ("CLOS", "Commentaire clos"),
                        ],
                        default="OUVERT",
                        max_length=25,
                    ),
                ),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("mis_a_jour_le", models.DateTimeField(auto_now=True)),
                ("resolu_le", models.DateTimeField(null=True)),
                ("clos_le", models.DateTimeField(null=True)),
                (
                    "convention",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="conventions.convention",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
