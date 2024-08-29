import uuid
from os.path import splitext

from django.db import models
from django.utils.text import slugify
from rest_framework import serializers


class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    filename = models.CharField(max_length=255)
    realname = models.CharField(max_length=255)

    dirpath = models.CharField(max_length=255, null=True)
    size = models.CharField(max_length=255, null=True)
    content_type = models.CharField(max_length=255, null=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def filepath(self, convention_uuid):
        if self.dirpath:
            filepath = f"{self.dirpath}/{self.uuid}_{self.filename}"
        else:
            filepath = (
                f"conventions/{convention_uuid}/media/" + f"{self.uuid}_{self.filename}"
            )
        return filepath

    def __str__(self):
        return self.filename

    def _compute_filename(self):
        if self.filename is None and self.realname is None:
            raise ValueError("filename or realname must be set")

        if self.filename is None:
            self.filename = self.realname
        else:
            self.realname = self.filename

        name, extension = splitext(self.filename)
        self.filename = f"{slugify(name)}{extension}"

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            self._compute_filename()
        return super().save(*args, **kwargs)


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"
