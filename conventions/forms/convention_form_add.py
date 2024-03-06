from django import forms

from programmes.models.choices import FinancementEDD


class ConventionAddForm(forms.Form):
    numero = forms.CharField(
        label="Numéro de la convention",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le numéro de la convention est obligatoire",
            "min_length": "Le numéro de la convention est obligatoire",
            "max_length": "Le numéro de la convention ne doit pas excéder 255 caractères",
        },
    )
    nb_logements = forms.IntegerField(
        label="Nombre de logements conventionnés",
        error_messages={
            "required": "Le nombre de logements conventionnés est obligatoire",
        },
    )
    financement = forms.TypedChoiceField(
        label="Type de financement",
        choices=FinancementEDD.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )
    annee_signature = forms.IntegerField(
        label="Année de signature de la convention",
    )
    nom_fichier_signe = forms.FileField(
        required=True,
    )
