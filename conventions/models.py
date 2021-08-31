import uuid
import datetime

from django.db import models
from programmes.models import Financement


class Convention(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=255)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey(
        "programmes.Programme", on_delete=models.CASCADE, null=False
    )
    lot = models.ForeignKey("programmes.Lot", on_delete=models.CASCADE, null=False)
    date_fin_conventionnement = models.DateField(null=True)
    financement = models.CharField(
        max_length=25,
        choices=Financement.choices,
        default=Financement.PLUS,
    )
    comments = models.TextField(null=True)
    soumis_le = models.DateTimeField(null=True)
    valide_le = models.DateTimeField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.programme.nom} - {self.lot.financement} - {self.programme.ville} - {self.programme.nb_logements} lgts"

    # TODO:
    # gérer un decorateur : https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#howto-custom-template-tags
    # Ou créé un champ statut
    def statut(self):
        if self.valide_le:
            return "Validé"
        elif self.soumis_le:
            return "En cours d'instruction"
        else:
            return "Brouillon"


class Preteur(models.TextChoices):
    ETAT = "ETAT", "Etat"
    EPCI = "EPCI", "EPCI"
    REGION = "REGION", "Région"
    CDCF = "CDCF", "CDC froncière"
    CDCL = "CDCL", "CDC locative"
    AUTRE = "AUTRE", "Autre"

class Pret(models.Model):
    import_mapping = {
        "Numéro": {"name": "numero"},
        "Date d'octroi": {"name": "date_octroi", "class": datetime.datetime},
        "Durée": {"name": "duree"},
        "Montant": {"name": "montant"},
        "Prêteur": {"name": "preteur", "class": Preteur},
        "Préciser l'identité du préteur si vous avez sélectionné 'Autre'": {
            "name": "autre"
        },
    }
    sheet_name = "Prêts"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    convention = models.ForeignKey("Convention", on_delete=models.CASCADE, null=False)
    preteur = models.CharField(
        max_length=25,
        choices=Preteur.choices,
        default=Preteur.AUTRE,
    )
    autre = models.CharField(null=True, max_length=255)
    date_octroi = models.DateField(null=True)
    numero = models.CharField(null=True, max_length=255)
    duree = models.IntegerField(null=True)
    montant = models.FloatField()
