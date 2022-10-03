from django.contrib import admin

from .models import Convention, Pret


@admin.display(description="Programme")
def view_programme(convention):
    return (
        f"{convention.programme.ville} -  {convention.lot} - "
        + f"{convention.lot.nb_logements} lgts - "
        + f"{convention.lot.get_type_habitat_display()}"
    )


class ConventionAdmin(admin.ModelAdmin):
    list_display = (view_programme, "administration", "bailleur", "financement", "uuid")
    search_fields = [
        "programme__ville",
        "programme__nom",
        "financement",
        "uuid",
        "bailleur__nom",
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
        "comments",
        "statut",
        "cree_par",
        "cree_le",
        "soumis_le",
        "premiere_soumission_le",
        "valide_le",
        "avenant_type",
        "donnees_validees",
        "nom_fichier_signe",
        "televersement_convention_signee_le",
        "date_resiliation",
    )
    list_select_related = (
        "programme",
        "lot",
        "bailleur",
    )
    readonly_fields = (
        "uuid",
        "bailleur",
        "programme",
        "lot",
        "administration",
        "parent",
        "cree_par",
        "cree_le",
    )


admin.site.register(Convention, ConventionAdmin)
admin.site.register(Pret)
