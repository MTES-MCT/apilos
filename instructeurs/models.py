import uuid

from django.db import models
from core.models import IngestableModel


class Administration(IngestableModel):
    def natural_key(self):
        return (self.code,)

    def get_by_natural_key(self, code):
        return self.get(code=code)

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
    adresse = models.TextField(null=True)
    code_postal = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    nb_convention_exemplaires = models.IntegerField(default=3)
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

    def _get_id(self):
        return self.id

    value = property(_get_id)

    def _get_nom(self):
        return self.nom

    label = property(_get_nom)
