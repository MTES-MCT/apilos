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
