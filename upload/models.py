import uuid

from rest_framework import serializers

from django.db import models

# Create your models here.
class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255, null=True)
    filepath = models.CharField(max_length=255, null=True, unique=True)
    #    image = models.ImageField(upload_to = 'image' , default = 'demo/demo.png')
    size = models.CharField(max_length=255, null=True)
    thumbnail = models.CharField(max_length=100000, blank=True, null=True)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     if not self.image:
    #         self.thumbnail = None
    #     else:
    #         thumbnail_size = 120, 120
    #         data_img = BytesIO()
    #         tiny_img = UploadedFiles.open(self.image)
    #         tiny_img.thumbnail(thumbnail_size)
    #         tiny_img.save(data_img, format="BMP")
    #         tiny_img.close()
    #         try:
    #             self.thumbnail = "data:image/jpg;base64,{}".format(
    #                 base64.b64encode(data_img.getvalue()).decode("utf-8")
    #             )
    #         except UnicodeDecodeError:
    #             self.blurred_image = None

    #     super(UploadedFiles, self).save(force_insert, force_update, using, update_fields)


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"
