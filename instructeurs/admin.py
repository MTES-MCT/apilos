from django.contrib import admin

from .models import (
    Administration,
)


class AdministrationAdmin(admin.ModelAdmin):
    search_fields = ["nom"]
    list_display = ["nom", "ville_signature"]


admin.site.register(Administration, AdministrationAdmin)
