from django.db import models


# TODO : remplir les champs
AVENANT_TYPE_FIELDS_MAPPING = {
    "denonciation": [
        "date_denonciation",
        "motif_denonciation",
        "fichier_instruction_denonciation",
    ],
    "champ_libre": [],
    "programme": ["programme.nom", "programme.adresse"],
    "commentaires": [],
    "duree": [],
    "bailleur": ["programme.bailleur.nom"],
}


class AvenantType(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255, unique=True)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom}"

    @classmethod
    def get_as_choices(cls):
        return [
            (avenant_type.nom, avenant_type.nom) for avenant_type in cls.objects.all()
        ]

    @property
    def fields(self):
        return AVENANT_TYPE_FIELDS_MAPPING.get(self.nom) or []
