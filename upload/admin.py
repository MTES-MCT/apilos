from django.contrib import admin

from admin.admin import ApilosModelAdmin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(ApilosModelAdmin):
    staff_user_can_change = False
    staff_user_can_add = False
    search_fields = ("filename", "realname", "uuid")
    list_display = ("filename", "realname", "uuid")
