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
    piece_jointe = models.TextField(blank=True)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.id and not self.survenu_le:
            # Définition de la data d'évènement à la date actuelle si omise à la création
            self.survenu_le = timezone.now()

        super().save(force_insert, force_update, using, update_fields)
