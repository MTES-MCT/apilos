from django.contrib import admin

# Register your models here.
from .models import Bailleur, Signataire, SignatairePardefaut


class BailleurAdmin(admin.ModelAdmin):
    search_fields = ["nom"]
    list_display = ["nom", "type_bailleur", "ville"]


admin.site.register(Bailleur, BailleurAdmin)


class SignataireAdmin(admin.ModelAdmin):
    search_fields = ["nom", "bailleur"]
    list_display = ["nom", "bailleur"]


admin.site.register(Signataire, SignataireAdmin)


class SignatairePardefautAdmin(admin.ModelAdmin):
    search_fields = ["bailleur"]
    list_display = ["bailleur"]


admin.site.register(SignatairePardefaut, SignatairePardefautAdmin)
