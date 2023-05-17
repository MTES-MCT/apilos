from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from bailleurs.models import Bailleur
from conventions.forms.convention_form_bailleur import ConventionBailleurForm


class BailleurForm(ConventionBailleurForm):
    nom = forms.CharField(
        required=True,
        label="Nom du bailleur",
        help_text="Tel qu'il sera affiché dans la convention",
        error_messages={
            "required": "Le nom du bailleur est obligatoire",
            "max_length": "Le nom du bailleur ne doit pas excéder 255 caractères",
        },
    )
    siret = forms.CharField(
        label="SIRET",
        min_length=7,
        max_length=14,
        error_messages={
            "required": "Le SIRET du bailleur est obligatoire",
            "max_length": "Le SIRET doit comporter 14 caractères",
            "min_length": "Le SIRET doit comporter 14 caractères",
        },
    )
    siren = forms.CharField(
        label="SIREN",
        required=False,
    )

    def clean_siret(self):
        siret = self.cleaned_data["siret"]
        if (
            Bailleur.objects.filter(siret=siret)
            .exclude(uuid=self.cleaned_data["uuid"])
            .exists()
        ):
            raise ValidationError(
                "Le siret du bailleur existe déjà, il doit-être unique"
            )
        return siret

    capital_social = forms.FloatField(
        required=False,
        label="Capital social",
    )

    adresse = forms.CharField(
        label="Adresse",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "L'adresse est obligatoire",
            "min_length": "L'adresse est obligatoire",
            "max_length": "L'adresse ne doit pas excéder 255 caractères",
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

    bailleur = forms.ModelChoiceField(
        required=False,
        label="Bailleur parent",
        help_text="Les utilisateurs du bailleur parent à les mêmes droits sur ce bailleur",
        initial=None,
        queryset=Bailleur.objects.none(),
        to_field_name="uuid",
    )

    def __init__(self, *args, bailleur_query: QuerySet, **kwargs) -> None:
        self.declared_fields["bailleur"].queryset = bailleur_query

        super().__init__(*args, **kwargs)
