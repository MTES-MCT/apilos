from django.contrib import admin

# Register your models here.
from .models import UploadedFile

admin.site.register(UploadedFile)
