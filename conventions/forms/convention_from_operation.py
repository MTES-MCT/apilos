from django import forms
from django.forms import BaseFormSet

from conventions.models.avenant_type import AvenantType
from programmes.models.choices import FinancementEDD


class AddConventionForm(forms.Form):
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


class AddAvenantForm(forms.Form):
    uuid = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    numero = forms.CharField(
        label="Numéro de l'avenant",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le numéro de la convention est obligatoire",
            "min_length": "Le numéro de la convention est obligatoire",
            "max_length": "Le numéro de la convention ne doit pas excéder 255 caractères",
        },
    )

    avenant_type = forms.ChoiceField(
        label="Objet de l'avenant",
        choices=AvenantType.get_as_detailed_choices,
        error_messages={
            "required": "Le type d'avenant est obligatoire",
        },
        required=True,
    )

    annee_signature = forms.IntegerField(
        label="Année de signature de l'avenant",
    )

    nom_fichier_signe = forms.FileField(
        required=False,
    )

    def _post_clean(self):
        if self.cleaned_data.get("uuid") and not self.cleaned_data.get(
            "nom_fichier_signe"
        ):
            self.add_error("nom_fichier_signe", "Le fichier signé est obligatoire")


class AddAvenantFormSet(BaseFormSet):
    pass
