from django.db import models


class TypeRole(models.TextChoices):
    INSTRUCTEUR = "INSTRUCTEUR", "Instructeur"
    BAILLEUR = "BAILLEUR", "Bailleur"
    # Administration centrale et direction régionale
    ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"


class EmailPreferences(models.TextChoices):
    # Toutes les conventions : L'utilisateur reçoit tous les emails pour toutes les conventions
    # dans son périmètre (selon ses filtres géographiques s'ils sont configurés)
    TOUS = "TOUS", "Tous les emails"
    # L'utilisateur reçoit tous les emails des conventions qu'il instruit
    # L'utilisateur instructeur reçoit les emails des conventions nouvellement à instruire
    PARTIEL = "PARTIEL", "Emails des conventions instruites"
    # L'utilisateur ne reçoit pas les emails relatifs aux conventions
    AUCUN = "AUCUN", "Aucun email"
