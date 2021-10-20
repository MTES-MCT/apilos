import uuid

from rest_framework import serializers

from django.db import models

# Create your models here.
class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255, null=True)
    dirpath = models.CharField(max_length=255, null=True)
    size = models.CharField(max_length=255, null=True)
    content_type = models.CharField(max_length=255, null=True)

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
