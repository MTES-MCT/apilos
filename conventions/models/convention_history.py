import uuid

from django.db import models

from conventions.models.choices import ConventionStatut


class ConventionHistory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        null=False,
        related_name="conventionhistories",
    )
    statut_convention = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    statut_convention_precedent = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    commentaire = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        "users.User",
        related_name="valide_par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
