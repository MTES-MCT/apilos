from django.contrib import admin

from admin.admin import ApilosModelAdmin
from bailleurs.models import Bailleur
from instructeurs.models import Administration
from programmes.models.models import IndiceEvolutionLoyer

from .models import (
    Annexe,
    Logement,
    Lot,
    Programme,
    ReferenceCadastrale,
    TypeStationnement,
)


@admin.register(Programme)
class ProgrammeAdmin(ApilosModelAdmin):
    list_display = ("nom", "uuid")
    fields = (
        "uuid",
        "nom",
        "adresse",
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


@admin.register(Lot)
class LotAdmin(ApilosModelAdmin):
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

    list_select_related = ("programme",)


@admin.register(Annexe)
class AnnexeAdmin(ApilosModelAdmin):
    list_select_related = ("logement",)
    readonly_fields = ("logement",)


@admin.register(Logement)
class LogementAdmin(ApilosModelAdmin):
    readonly_fields = ("lot",)
    list_display = (
        "id",
        "lot",
        "typologie",
        "designation",
    )


@admin.register(ReferenceCadastrale)
class ReferenceCadastraleAdmin(ApilosModelAdmin):
    readonly_fields = ("programme",)


@admin.register(TypeStationnement)
class TypeStationnementAdmin(admin.ModelAdmin):
    list_select_related = ("lot__programme",)
    readonly_fields = ("lot",)


@admin.register(IndiceEvolutionLoyer)
class IndiceEvolutionLoyerAdmin(ApilosModelAdmin):
    pass
