from django.contrib import admin
from admin.admin import ApilosModelAdmin

from .models import Convention, Pret, AvenantType


@admin.display(description="Programme")
def view_programme(convention):
    return (
        f"{convention.programme.ville} -  {convention.lot} - "
        + f"{convention.lot.nb_logements} lgts - "
        + f"{convention.lot.get_type_habitat_display()}"
    )


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
