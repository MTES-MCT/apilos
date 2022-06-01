import uuid

from django.db import models
from core.models import IngestableModel


class Administration(IngestableModel):

    pivot = "code"
    mapping = {
        "nom": "Gestionnaire",
        "code": "Gestionnaire (code)",
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    ville_signature = models.CharField(max_length=255, null=True)
    adresse = models.CharField(max_length=255, null=True)
    code_postal = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    prefix_convention = models.CharField(
        max_length=255, default="{département}/{zone}/{mois}/{année}/80.416/", null=True
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    def get_ville_signature_or_empty(self):
        return (
            self.ville_signature
            if self.ville_signature
            else "                              "
        )
