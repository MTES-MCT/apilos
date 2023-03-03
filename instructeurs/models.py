import uuid

from django.db import models

from apilos_settings.models import Departement
from core.models import IngestableModel


class AdministrateurManager(models.Manager):
    def get_by_natural_key(self, field, value):
        if field == "code":
            return self.get(code=value)

        return self.get(pk=value)


class Administration(IngestableModel):
    objects = AdministrateurManager()

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
    adresse = models.TextField(null=True, blank=True)
    code_postal = models.CharField(max_length=5, null=True, blank=True)
    ville = models.CharField(max_length=255, null=True, blank=True)
    nb_convention_exemplaires = models.IntegerField(default=3)
    prefix_convention = models.CharField(
        max_length=255, default="{département}/{zone}/{mois}/{année}/80.416/", null=True
    )
    signataire_bloc_signature = models.TextField(null=True, blank=True)
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

    def natural_key(self) -> tuple:
        return tuple(self.code)

    def get_departement_code(self) -> str:
        return self.code_postal[0:2]

    def is_ddt(self) -> bool:
        return self.code.startswith("DD")

    def _get_id(self):
        return self.id

    value = property(_get_id)

    def _get_nom(self):
        return self.nom

    label = property(_get_nom)
