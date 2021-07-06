from django.contrib import admin

from .models import Programme, ReferenceCadastrale, Lot, Logement, Annexe, TypeStationnement

admin.site.register(Programme)
admin.site.register(ReferenceCadastrale)
admin.site.register(Lot)
admin.site.register(Logement)
admin.site.register(Annexe)
admin.site.register(TypeStationnement)
