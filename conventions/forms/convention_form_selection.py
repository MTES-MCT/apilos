"""
Étape Selection du formulaire par étape de la convention
    - Selection d'un lot à conventionner
    - création d'un programme/lot/convention à partir de zéro
"""

from django import forms
from django.db.models import QuerySet

from bailleurs.models import Bailleur
from programmes.models import ActiveNatureLogement, FinancementEDD, TypeHabitat


class CreateConventionMinForm(forms.Form):
    def __init__(
        self, *args, bailleur_query: QuerySet, administrations=None, **kwargs
    ) -> None:
        self.declared_fields["administration"].choices = administrations
        self.declared_fields["bailleur"].queryset = bailleur_query

        super().__init__(*args, **kwargs)

    bailleur = forms.ModelChoiceField(
        label="Bailleur",
        queryset=Bailleur.objects.none(),
        to_field_name="uuid",
        error_messages={
            "required": "Le bailleur est obligatoire",
        },
    )
    administration = forms.ChoiceField(
        label="Administration",
        choices=[],
        help_text="L’administration est l’administration État soit les DDI.<br>"
        "Ne pas prendre l’administration <i>ANAH</i> ou <i>ANRU</i>.",
        error_messages={
            "required": "L'administration est obligatoire",
        },
    )
    nom = forms.CharField(
        label="Nom du programme",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom du programme est obligatoire",
            "min_length": "Le nom du programme est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 255 caractères",
        },
    )
    financement = forms.TypedChoiceField(
        label="Financement",
        choices=FinancementEDD.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )
    nature_logement = forms.ChoiceField(
        label="Nature des logements",
        help_text=(
            "Si la convention ne porte pas sur une résidence ou un foyer,"
            + " vous devez selectionner «Logements ordinaires»"
        ),
        choices=ActiveNatureLogement.choices,
        error_messages={
            "required": "La selection de la nature des logements est obligatoire"
        },
    )
    nb_logements = forms.IntegerField(
        label="Nb logements à conventionner",
        error_messages={
            "required": "Le nombre de logements à conventionner est obligatoire",
        },
    )
    code_postal = forms.CharField(
        label="Code postal",
        min_length=5,
        max_length=5,
        error_messages={
            "required": "Le code postal est obligatoire",
            "max_length": "Le code postal est une suite de 5 caractères",
            "min_length": "Le code postal est une suite de 5 caractères",
        },
    )
    ville = forms.CharField(
        label="Ville",
        max_length=255,
        error_messages={
            "required": "La ville est obligatoire",
            "max_length": "La ville ne doit pas excéder 255 caractères",
        },
    )


class NewConventionForm(CreateConventionMinForm):
    """
    Formulaire de création d'un programme/lot/convention à partir de zéro
    """

    numero_operation = forms.CharField(
        label="Numéro d'opération",
        required=True,
        max_length=255,
        error_messages={
            "max_length": "Le Numéro d'opération ne doit pas excéder 255 caractères",
        },
    )
    type_habitat = forms.TypedChoiceField(
        label="Type d'habitat",
        choices=TypeHabitat.choices,
        error_messages={
            "required": "Le type d'habitat est obligatoire",
        },
    )


class ConventionForAvenantForm(CreateConventionMinForm):
    """
    Formulaire de création d'un programme/lot/convention pour un avenant sur une convention
      non-connue d'APiLos
    """

    nature_logement = forms.ChoiceField(
        label="Nature des logements",
        help_text=(
            "Si la convention ne porte pas sur une résidence ou un foyer,"
            + " vous devez selectionner «Logements ordinaires»"
        ),
        choices=ActiveNatureLogement.choices,
        initial=ActiveNatureLogement.LOGEMENTSORDINAIRES,
        error_messages={
            "required": "La selection de la nature des logements est obligatoire"
        },
    )

    statut = forms.CharField(
        required=False,
    )
    numero = forms.CharField(
        label="Numéro de convention",
    )
    nom_fichier_signe = forms.FileField(
        required=False,
    )
    numero_avenant = forms.CharField(
        label="Numéro de l'avenant à créer",
    )
