from django import forms

from programmes.models import FinancementEDD, TypeHabitat


class ProgrammeSelectionFromDBForm(forms.Form):
    def __init__(self, *args, lots=None, **kwargs) -> None:
        self.declared_fields["lot"].choices = lots
        super().__init__(*args, **kwargs)

    lot = forms.ChoiceField(
        label="Lot à conventionner",
        choices=[],
        error_messages={
            "required": "La selection du programme et de son financement est obligatoire"
        },
    )


class ProgrammeSelectionFromZeroForm(forms.Form):
    def __init__(self, *args, bailleurs=None, administrations=None, **kwargs) -> None:
        self.declared_fields["bailleur"].choices = bailleurs
        self.declared_fields["administration"].choices = administrations
        super().__init__(*args, **kwargs)

    bailleur = forms.ChoiceField(
        label="Bailleur",
        choices=[],
        error_messages={
            "required": "Le bailleur est obligatoire",
        },
    )
    administration = forms.ChoiceField(
        label="Administration",
        choices=[],
        help_text="Délégataire des aides à la pierre du territoire de l'opération",
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
    nb_logements = forms.IntegerField(
        label="Nb logements à conventionner",
        error_messages={
            "required": "Le nombre de logements à conventionner est obligatoire",
        },
    )
    type_habitat = forms.TypedChoiceField(
        label="Type d'habitat",
        choices=TypeHabitat.choices,
        error_messages={
            "required": "Le type d'habitat est obligatoire",
        },
    )
    financement = forms.TypedChoiceField(
        label="Financement",
        choices=FinancementEDD.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )
    code_postal = forms.CharField(
        label="Code postal",
        max_length=255,
        error_messages={
            "required": "Le code postal est obligatoire",
            "max_length": "Le code postal ne doit pas excéder 255 caractères",
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
    statut = forms.CharField(
        required=False,
    )
    numero = forms.CharField(
        required=False,
        label="Numéro de convention",
    )
    nom_fichier_signe = forms.FileField(
        required=False,
    )
