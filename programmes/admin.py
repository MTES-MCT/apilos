from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from admin.admin import ApilosModelAdmin
from admin.filters import IsCloneFilter
from bailleurs.models import Bailleur
from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import IndiceEvolutionLoyer

from .models import (
    Annexe,
    Logement,
    Lot,
    Programme,
    ReferenceCadastrale,
    TypeStationnement,
)


class ConventionInline(admin.StackedInline):
    model = Convention
    fields = ("uuid", "get_statut", "financement", "lot")
    readonly_fields = (
        "uuid",
        "get_statut",
    )
    show_change_link = True
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Statut")
    def get_statut(self, obj):
        return obj.statut


@admin.register(Programme)
class ProgrammeAdmin(ApilosModelAdmin):
    list_display = (
        "nom",
        "uuid",
        "numero_operation",
        "ville",
        "nature_logement",
    )
    fields = (
        "uuid",
        "nom",
        "adresse",
        "code_postal",
        "ville",
        "numero_operation",
        "numero_operation_pour_recherche",
        "administration",
        "bailleur",
        "zone_123",
        "zone_abc",
        "nature_logement",
        "date_achevement",
        "surface_utile_totale",
        "type_operation",
        "search_vector",
    )
    readonly_fields = (
        "uuid",
        "search_vector",
        "numero_operation_pour_recherche",
    )
    autocomplete_fields = ("administration", "bailleur")
    list_filter = (
        IsCloneFilter,
        "nature_logement",
    )
    search_fields = (
        "nom",
        "adresse",
        "code_postal",
        "ville",
        "numero_operation",
        "uuid",
    )

    inlines = (ConventionInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "administration":
            kwargs["queryset"] = Administration.objects.order_by("nom")
        if db_field.name == "bailleur":
            kwargs["queryset"] = Bailleur.objects.order_by("nom")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.display(description="Programme")
def view_programme(lot):
    return f"{lot.programme.ville} -  {lot.programme.nom}"


@admin.register(Lot)
class LotAdmin(ApilosModelAdmin):
    list_display = (view_programme, "financement", "uuid")

    list_select_related = ("programme",)

    search_fields = [
        "programme__ville",
        "programme__nom",
        "programme__numero_operation",
        "financement",
        "uuid",
    ]

    fields = (
        "uuid",
        "financement",
        "nb_logements",
        "type_habitat",
        "programme",
    )

    readonly_fields = ("uuid",)

    autocomplete_fields = ("programme",)


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
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("departements")

    list_display = (
        "uuid",
        "annee",
        "date_debut",
        "date_fin",
        "is_loyer",
        "nature_logement",
        "evolution",
        "liste_departements",
    )

    def liste_departements(self, obj):
        return "\n".join([d.nom for d in obj.departements.all()])

    list_filter = (
        "is_loyer",
        "nature_logement",
    )

    search_fields = ("annee",)
