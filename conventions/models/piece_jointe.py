import uuid

from django.db import models


class PieceJointeType(models.TextChoices):
    CONVENTION = "CONVENTION", "Convention APL"
    RECTIFICATION = (
        "RECTIFICATION",
        "Demande de rectification(s) du bureau des hypothèques",
    )
    ATTESTATION_PREFECTORALE = "ATTESTATION_PREFECTORALE", "Attestations préfectorales"
    AVENANT = "AVENANT", "Avenant"
    PHOTO = "PHOTO", "Photographie du bâti ou des logements"
    AUTRE = "AUTRE", "Autre"


class PieceJointe(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        null=False,
        related_name="pieces_jointes",
    )
    type = models.CharField(
        null=True,
        max_length=24,
        choices=PieceJointeType.choices,
        default=PieceJointeType.AUTRE,
    )
    fichier = models.CharField(null=True, blank=True, max_length=50)
    nom_reel = models.CharField(null=True, blank=True, max_length=255)
    description = models.CharField(null=True, blank=True, max_length=1000)
    cree_le = models.DateTimeField(auto_now_add=False)

    def is_convention(self) -> bool:
        return self.type == PieceJointeType.CONVENTION
