from django.db import models


class DepartementManager(models.Manager):
    def get_by_natural_key(self, code_insee, _):
        return self.get(code_insee=code_insee)


class Departement(models.Model):

    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255, unique=True)
    code_insee = models.CharField(max_length=3, unique=True)
    code_insee_region = models.CharField(max_length=2)
    code_postal = models.CharField(max_length=3)

    objects = DepartementManager()

    def natural_key(self) -> tuple:
        return tuple(self.code_insee)

    def __str__(self) -> str:
        return f"{self.code_insee} - {self.nom}"


# Not a table in DB, only used to handle excel upload on delegataires
class Commune(models.Model):
    code_postal = models.CharField(max_length=5, blank=True)
    commune = models.CharField(max_length=255, blank=True)
    # Needed to import xlsx files
    import_mapping = {
        "Code postal": "code_postal",
        "Commune": "commune",
    }
    sheet_name: str = "Communes"

    class Meta:
        managed = False
