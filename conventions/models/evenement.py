import uuid

from django.db import models
from django.utils import timezone

from conventions.models import TypeEvenement


class Evenement(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        null=False,
        related_name="evenements",
    )
    type_evenement = models.CharField(
        max_length=50,
        choices=TypeEvenement.choices,
        default=TypeEvenement.DEPOT_BAILLEUR,
    )
    survenu_le = models.DateField(editable=False)
    description = models.TextField(null=True, blank=True)
    pieces_jointes = models.TextField(blank=True)

    def save(self, *args, **kwargs) -> None:
        if not self.id and not self.survenu_le:
            # Définition de la data d'évènement à la date actuelle si omise à la création
            self.survenu_le = timezone.now()
        super().save(*args, **kwargs)
