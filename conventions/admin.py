from django import forms
from django.contrib import admin
from django.contrib.admin import ChoicesFieldListFilter
from django.core.exceptions import ValidationError

from admin.admin import ApilosModelAdmin
from admin.filters import IsCloneFilter
from conventions.models.choices import ConventionStatut

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

        try:
            self.instance.validate_constraints()
        except ValidationError as err:
            if "unique_display_name" in str(err):
                self.add_error(
                    None,
                    (
                        "Problème d'unicité, une convention existe déjà pour ces critères. "
                        f"Vérifiez les conventions existantes sur le programme {self.instance.programme.id}, "
                        "le lot {self.instance.lot.id}, "
                        f"avec un financement {self.instance.financement}."
                    ),
                )
            else:
                self.add_error(None, err)

    class Meta:
        model = Convention
        exclude = []


@admin.display(description="Numero d'opération")
def view_programme_operation(convention):
    return convention.programme.numero_galion


@admin.register(Convention)
class ConventionAdmin(ApilosModelAdmin):
    list_display = (
        view_programme,
        "administration",
        "bailleur",
        "financement",
        "uuid",
        view_programme_operation,
    )
    search_fields = [
        "programme__ville",
        "programme__nom",
        "financement",
        "uuid",
        "programme__bailleur__nom",
        "programme__administration__nom",
        "programme__numero_galion",
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
        ("statut", StatutFilter),
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
