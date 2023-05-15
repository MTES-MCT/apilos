from django.contrib import admin

from bailleurs.models import Bailleur
from instructeurs.models import Administration

from .models import (
    Annexe,
    Logement,
    Lot,
    Programme,
    ReferenceCadastrale,
    TypeStationnement,
)


class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("nom", "uuid")
    fields = (
        "uuid",
        "nom",
        "code_postal",
        "ville",
        "numero_galion",
        "administration",
        "bailleur",
        "zone_123",
        "zone_abc",
    )
    readonly_fields = (
        "uuid",
        "administration",
        "bailleur",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "administration":
            kwargs["queryset"] = Administration.objects.order_by("nom")
        if db_field.name == "bailleur":
            kwargs["queryset"] = Bailleur.objects.order_by("nom")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    search_fields = ["nom"]


@admin.display(description="Programme")
def view_programme(lot):
    return f"{lot.programme.ville} -  {lot.programme.nom}"


class LotAdmin(admin.ModelAdmin):
    list_display = (view_programme, "financement", "uuid")

    fields = (
        "uuid",
        "financement",
        "nb_logements",
        "type_habitat",
        "programme",
    )

    readonly_fields = (
        "uuid",
        "programme",
    )


admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(ReferenceCadastrale)
admin.site.register(Lot, LotAdmin)
admin.site.register(Logement)
admin.site.register(Annexe)
admin.site.register(TypeStationnement)
