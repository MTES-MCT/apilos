from django.contrib import admin

from .models import (
    Administration,
)


class AdministrationAdmin(admin.ModelAdmin):
    search_fields = ["nom", "code"]
    list_display = ["nom", "code", "ville_signature"]


admin.site.register(Administration, AdministrationAdmin)
