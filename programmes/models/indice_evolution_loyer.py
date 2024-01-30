import uuid

from django.db import models

from .choices import (
    NatureLogement,
)


class IndiceEvolutionLoyer(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=["annee", "is_loyer", "nature_logement"],
                name="idx_annee_and_type",
            ),
        ]

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    is_loyer = models.BooleanField(default=True)
    annee = models.IntegerField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    nature_logement = models.TextField(
        choices=NatureLogement.choices,
        default=NatureLogement.LOGEMENTSORDINAIRES,
        null=True,
    )
    # Evolution, en pourcentage
    evolution = models.FloatField()

    def __str__(self):
        return f"{self.annee} / {self.nature_logement} => {self.evolution}"
