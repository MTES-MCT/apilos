from django.contrib import admin

from bailleurs.models import Bailleur
from instructeurs.models import Administration

from .models import (
    Programme,
    ReferenceCadastrale,
    Lot,
    Logement,
    Annexe,
    TypeStationnement,
)


class ProgrammeAdmin(admin.ModelAdmin):
    exclude = (
        "zone_123",
        "zone_abc",
        "vendeur",
        "acquereur",
        "date_acte_notarie",
        "reference_notaire",
        "reference_publication_acte",
        "acte_de_propriete",
        "acte_notarial",
        "reference_cadastrale",
        "edd_volumetrique",
        "mention_publication_edd_volumetrique",
        "edd_classique",
        "mention_publication_edd_classique",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "administration":
            kwargs["queryset"] = Administration.objects.order_by("nom")
        if db_field.name == "bailleur":
            kwargs["queryset"] = Bailleur.objects.order_by("nom")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    search_fields = ["nom"]


admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(ReferenceCadastrale)
admin.site.register(Lot)
admin.site.register(Logement)
admin.site.register(Annexe)
admin.site.register(TypeStationnement)
