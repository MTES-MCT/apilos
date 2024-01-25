from typing import Any

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from admin.admin import ApilosModelAdmin
from admin.filters import IsCloneFilter
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
    list_display = (
        "nom",
        "uuid",
        "numero_galion",
    )
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
    list_filter = (IsCloneFilter,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "administration":
            kwargs["queryset"] = Administration.objects.order_by("nom")
        if db_field.name == "bailleur":
            kwargs["queryset"] = Bailleur.objects.order_by("nom")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    search_fields = ["nom", "uuid", "numero_galion"]


@admin.display(description="Programme")
def view_programme(lot):
    return f"{lot.programme.ville} -  {lot.programme.nom}"


class HasConvention(SimpleListFilter):
    title = "lié à une convention"
    parameter_name = "has_convention"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> list[tuple[Any, str]]:
        return (
            ("Oui", "Oui"),
            ("Non", "Non"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        queryset = queryset.annotate(convention_count=Count("conventions"))
        match self.value():
            case "Oui":
                return queryset.filter(convention_count__gt=0)
            case "Non":
                return queryset.filter(convention_count__lte=0)
            case _:
                return queryset


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

    list_filter = (HasConvention,)


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
    list_display = (
        "uuid",
        "annee",
        "date_debut",
        "date_fin",
        "is_loyer",
        "nature_logement",
        "evolution",
    )

    list_filter = (
        "is_loyer",
        "nature_logement",
    )

    search_fields = ("annee",)
