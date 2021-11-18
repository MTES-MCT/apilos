from django.db import models


class TypeRole(models.TextChoices):
    INSTRUCTEUR = "INSTRUCTEUR", "Instructeur"
    BAILLEUR = "BAILLEUR", "Bailleur"
