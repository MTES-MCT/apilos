from django.contrib import admin

from admin.admin import ApilosModelAdmin

from .models import Bailleur


@admin.register(Bailleur)
class BailleurAdmin(ApilosModelAdmin):
    search_fields = [
        "nom",
    ]
    list_display = [
        "nom",
        "nature_bailleur",
        "sous_nature_bailleur",
        "ville",
    ]
    readonly_fields = ("parent",)
