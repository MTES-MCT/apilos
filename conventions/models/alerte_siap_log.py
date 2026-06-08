import uuid

from django.db import models


class AlerteSIAPStatut(models.TextChoices):
    ENVOYEE = "ENVOYEE", "Envoyée"
    ECHEC = "ECHEC", "Échec"


class AlerteSIAPOperation(models.TextChoices):
    CREATION = "CREATION", "Création"
    SUPPRESSION = "SUPPRESSION", "Suppression"


class AlerteSIAPLog(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        related_name="alerte_siap_logs",
    )
    operation = models.CharField(
        max_length=15,
        choices=AlerteSIAPOperation.choices,
    )
    statut = models.CharField(
        max_length=10,
        choices=AlerteSIAPStatut.choices,
    )
    description = models.CharField(max_length=255)
    destinataires = models.JSONField(default=list, blank=True)
    etiquette = models.CharField(max_length=255, blank=True, default="")
    user_login = models.CharField(max_length=255, blank=True, default="")
    habilitation_id = models.CharField(max_length=255, blank=True, default="")
    erreur = models.TextField(blank=True, default="")
    payload = models.JSONField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "Log alerte SIAP"
        verbose_name_plural = "Logs alertes SIAP"

    def __str__(self):
        return f"[{self.statut}] {self.operation} - {self.description} ({self.convention_id})"
