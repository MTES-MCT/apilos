from django import forms
from django.db.models import QuerySet

from bailleurs.models import Bailleur
from programmes.models.choices import FinancementEDD


class AddConventionForm(forms.Form):

    def __init__(self, *args, financements: list[tuple[str, str]], **kwargs) -> None:
        self.declared_fields["financement"].choices = financements
        super().__init__(*args, **kwargs)

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
    def __init__(self, *args, bailleur_query: QuerySet[Bailleur], **kwargs) -> None:
        self.declared_fields["bailleur"].queryset = bailleur_query
        super().__init__(*args, **kwargs)

    numero = forms.CharField(
        label="Numéro de l'avenant",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le numéro de la convention est obligatoire",
            "min_length": "Le numéro de la convention est obligatoire",
            "max_length": "Le numéro de la convention ne doit pas excéder 255 caractères",
        },
        required=True,
    )

    annee_signature = forms.IntegerField(
        label="Année de signature de l'avenant",
        required=True,
    )

    nom_fichier_signe = forms.FileField(
        required=True,
    )

    bailleur = forms.ModelChoiceField(
        label="Bailleur suite à cet avenant",
        queryset=Bailleur.objects.none(),
        to_field_name="uuid",
        required=False,
    )

    champ_libre_avenant = forms.CharField(
        label="Renseignements supplémentaires suite à cet avenant",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
        required=False,
        empty_value=None,
    )

    nb_logements = forms.IntegerField(
        label="Nombre de logements suite à cet avenant",
        required=False,
    )
