from django.db import models
from django.conf import settings

from rest_framework import serializers


def upload_to(convention, filename):
    return f"{convention.uuid}/{convention.field_name}/{filename}"


class FileManager(models.Manager):
    def commentaires(self):
        return self.filter(field_name=File.FieldName.COMMENTAIRES)


class File(models.Model):
    objects = FileManager()

    class FieldName(models.TextChoices):
        COMMENTAIRES = "COMMENTAIRES", "Commentaires"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    file = models.FileField("Fichier", upload_to=upload_to, blank=False, null=False)
    field_name = models.CharField(
        choices=FieldName.choices, help_text="Le nom du champ dans la convention"
    )
    convention = models.ForeignKey(
        "conventions.Convention",
        related_name="files",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
