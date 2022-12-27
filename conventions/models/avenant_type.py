from django.db import models


class AvenantType(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255, unique=True)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom}"

    @classmethod
    def get_as_choices(cls):
        return [
            (avenant_type.nom, avenant_type.nom) for avenant_type in cls.objects.all()
        ]
