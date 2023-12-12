from django.contrib import admin
from admin.admin import ApilosModelAdmin

from .models import Administration


@admin.register(Administration)
class AdministrationAdmin(ApilosModelAdmin):
    search_fields = ["nom", "code"]
    list_display = ["nom", "code", "ville_signature"]
