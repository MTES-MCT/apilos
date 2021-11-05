import uuid

from django.db import models


class CommentStatut(models.TextChoices):
    # Le commentaire est ouvert par l'instructeur - Affichage en rouge
    OUVERT = "OUVERT", "Ouvert"
    # Le commentaire a été marqué comme résolu par le bailleur - Affichage en vert
    RESOLU = "RESOLU", "Résolu"
    # L'instructeur a clos le commentaire - Par d'affichage
    CLOS = "CLOS", "Commentaire clos"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nom_objet = models.CharField(max_length=255)
    champ_objet = models.CharField(max_length=255)
    uuid_objet = models.UUIDField(max_length=255)
    convention = models.ForeignKey(
        "conventions.Convention", on_delete=models.CASCADE, null=False
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False)
    message = models.TextField(null=True)
    statut = models.CharField(
        max_length=25,
        choices=CommentStatut.choices,
        default=CommentStatut.OUVERT,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
    resolu_le = models.DateTimeField(null=True)
    clos_le = models.DateTimeField(null=True)
