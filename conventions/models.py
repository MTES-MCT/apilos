from django.db import models

import uuid

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
            return 'Validé'
        elif self.soumis_le:
            return "En cours d'instruction"
        else:
            return "Brouillon"


class Pret(models.Model):
    class Preteur(models.TextChoices):
        ETAT = "ETAT", "Etat"
        EPCI = "EPCI", "EPCI"
        REGION = "REGION", "Region"
        CDCF = "CDCF", "Caisse des dépots et des consignations Froncière"
        CDCL = "CDCL", "Caisse des dépots et des consignations Locative"
        AUTRE = "AUTRE", "Autre"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    convention = models.ForeignKey("Convention", on_delete=models.CASCADE, null=False)
    preteur = models.CharField(
        max_length=25,
        choices=Preteur.choices,
        default=Preteur.CDCF,
    )
    autre = models.CharField(max_length=255)
    date_octroi = models.DateField()
    numero = models.CharField(max_length=255)
    duree = models.IntegerField()
    montant = models.FloatField()
