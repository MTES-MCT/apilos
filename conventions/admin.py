from django import forms
from django.contrib import admin
from django.contrib.admin import ChoicesFieldListFilter, TabularInline
from django.urls import reverse
from django.utils.html import format_html

from admin.admin import ApilosModelAdmin
from admin.filters import IsCloneFilter
from conventions.models.choices import ConventionStatut
from conventions.models.piece_jointe import PieceJointe

from .models import AvenantType, Convention, Pret


@admin.display(description="Programme")
def view_programme(convention):

    return (
        f"{convention.programme.ville} -  {convention.lot} - "
        + f"{convention.lot.nb_logements} lgts - "
        + f"{convention.lot.get_type_habitat_display()}"
    )


class IsAvenantFilter(IsCloneFilter):
    title = "est un avenant"
    parameter_name = "is_avenant"


class StatutFilter(ChoicesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.used_parameters and self.lookup_kwarg in self.used_parameters:
            self.used_parameters[self.lookup_kwarg] = ConventionStatut[
                self.used_parameters[self.lookup_kwarg]
            ].label


class ConventionModelForm(forms.ModelForm):
    statut = forms.ChoiceField(choices=ConventionStatut.choices)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", {})

        instance = kwargs.get("instance", None)
        if instance:
            statut = ConventionStatut.get_by_label(instance.statut)
            if statut:
                initial["statut"] = statut.name

        super().__init__(*args, initial=initial, **kwargs)

    def _post_clean(self) -> None:
        super()._post_clean()

        self.instance.statut = ConventionStatut[self.instance.statut].label

    class Meta:
        model = Convention
        exclude = []


@admin.display(description="Numero d'opération")
def view_programme_operation(convention):
    return convention.programme.numero_operation


class PieceJointeInline(TabularInline):
    model = PieceJointe
    extra = 0

    readonly_fields = fields = (
        "id",
        "uuid",
        "type",
        "fichier_link",
        "nom_reel",
        "description",
        "cree_le",
    )

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return True

    def fichier_link(self, obj):
        if obj.fichier:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                reverse("conventions:piece_jointe", args=[obj.uuid]),
                obj.fichier,
            )
        return "-"


@admin.register(Convention)
class ConventionAdmin(ApilosModelAdmin):
    list_display = (
        "__str__",
        "administration",
        "bailleur",
        "uuid",
        "numero",
        view_programme_operation,
    )
    search_fields = [
        "programme__ville",
        "programme__nom",
        "uuid",
        "numero_pour_recherche",
        "programme__bailleur__nom",
        "programme__administration__nom",
        "programme__numero_operation",
    ]
    fields = (
        "uuid",
        "administration",
        "bailleur",
        "programme",
        "lot",
        "numero",
        "numero_pour_recherche",
        "date_fin_conventionnement",
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
        "date_envoi_spf",
        "date_publication_spf",
        "desc_avenant",
        "champ_libre_avenant",
        "date_denonciation",
        "motif_denonciation",
        "adresse",
        "parent",
    )
    list_select_related = (
        "programme__bailleur",
        "programme__administration",
    )
    readonly_fields = (
        "uuid",
        "bailleur",
        "administration",
        "numero_pour_recherche",
        "cree_par",
        "cree_le",
        "lot",
    )
    autocomplete_fields = (
        "programme",
        "parent",
    )
    list_filter = (
        IsAvenantFilter,
        ("statut", StatutFilter),
        "cree_le",
    )

    form = ConventionModelForm
    inlines = [PieceJointeInline]

    @admin.display(description="Lot")
    def lot(self, obj):
        return obj.lot


@admin.register(Pret)
class PretAdmin(ApilosModelAdmin):
    list_display = (
        "id",
        "lot",
        "preteur",
        "date_octroi",
        "numero",
        "montant",
    )
    readonly_fields = ("lot",)


@admin.register(AvenantType)
class AvenantTypeAdmin(ApilosModelAdmin):
    staff_user_can_change = False
    staff_user_can_add = False
