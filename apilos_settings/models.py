from django.db import models


class Departement(models.Model):

    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255, unique=True)
    code_insee = models.CharField(max_length=3, unique=True)
    code_postal = models.CharField(max_length=3)

    def natural_key(self):
        return (self.code_insee,)

    def get_by_natural_key(self, code_insee):
        return self.get(code_insee=code_insee)

    def __str__(self) -> str:
        return f"{self.code_insee} - {self.nom}"
