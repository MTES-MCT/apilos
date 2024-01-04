from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import QuerySet
from django.http import HttpRequest

from admin.admin import ApilosModelAdmin
from conventions.models.choices import ConventionStatut

from .models import AvenantType, Convention, Pret


@admin.display(description="Programme")
def view_programme(convention):
    return (
        f"{convention.programme.ville} -  {convention.lot} - "
        + f"{convention.lot.nb_logements} lgts - "
        + f"{convention.lot.get_type_habitat_display()}"
    )


class IsAvenantFilter(SimpleListFilter):
    title = "type avenant"
    parameter_name = "is_avenant"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> list[tuple[Any, str]]:
        return (
            ("Oui", "Oui"),
            ("Non", "Non"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        match self.value():
            case "Oui":
                return queryset.filter(parent__isnull=False)
            case "Non":
                return queryset.filter(parent__isnull=True)
            case _:
                return queryset


class ConventionModelForm(forms.ModelForm):
    statut = forms.ChoiceField(choices=ConventionStatut.choices)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", {})

        instance = kwargs.get("instance", None)
        if instance:
            statut = ConventionStatut.get_by_label(instance.statut)
            if statut:
                initial["statut"] = statut.name

        super().__init__(initial=initial, *args, **kwargs)

    def _post_clean(self):
        super()._post_clean()
        statut = self.cleaned_data.get("statut")
        self.cleaned_data["statut"] = ConventionStatut[statut].label

    class Meta:
        model = Convention
        exclude = []


@admin.register(Convention)
class ConventionAdmin(ApilosModelAdmin):
    list_display = (view_programme, "administration", "bailleur", "financement", "uuid")
    search_fields = [
        "programme__ville",
        "programme__nom",
        "financement",
        "uuid",
        "programme__bailleur__nom",
        "programme__administration__nom",
    ]
    fields = (
        "uuid",
        "administration",
        "bailleur",
        "programme",
        "lot",
        "parent",
        "numero",
        "date_fin_conventionnement",
        "financement",
        "fond_propre",
        "commentaires",
        "statut",
        "cree_par",
        "cree_le",
        "soumis_le",
        "premiere_soumission_le",
        "valide_le",
        "avenant_types",
        "donnees_validees",
        "nom_fichier_signe",
        "televersement_convention_signee_le",
        "date_resiliation",
        "desc_avenant",
        "champ_libre_avenant",
        "date_denonciation",
        "motif_denonciation",
        "adresse",
    )
    list_select_related = (
        "programme__bailleur",
        "programme__administration",
        "lot__programme",
    )
    readonly_fields = (
        "uuid",
        "programme",
        "bailleur",
        "lot",
        "administration",
        "parent",
        "cree_par",
        "cree_le",
    )
    list_filter = (
        IsAvenantFilter,
        "cree_le",
    )

    form = ConventionModelForm


@admin.register(Pret)
class PretAdmin(ApilosModelAdmin):
    list_display = (
        "id",
        "convention",
        "preteur",
        "date_octroi",
        "numero",
        "montant",
    )
    readonly_fields = ("convention",)


@admin.register(AvenantType)
class AvenantTypeAdmin(ApilosModelAdmin):
    staff_user_can_change = False
    staff_user_can_add = False
