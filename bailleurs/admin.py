from django.contrib import admin

# Register your models here.
from .models import Bailleur


class BailleurAdmin(admin.ModelAdmin):
    search_fields = ["nom"]
    list_display = ["nom", "nature_bailleur", "sous_nature_bailleur", "ville"]


admin.site.register(Bailleur, BailleurAdmin)
