import uuid

from django.db import models
from rest_framework import serializers


# Create your models here.
class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255, null=True)
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


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"
