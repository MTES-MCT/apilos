from django import forms
from core import forms_utils


class BailleurForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    nom = forms.CharField(
        required=True,
        error_messages={
            "required": "Le nom du bailleur est obligatoire",
            "max_length": "Le nom du bailleur ne doit pas excéder 255 caractères",
        },
    )
    siret = forms.CharField(
        max_length=14,
        min_length=9,
        error_messages={
            "required": "Le SIRET ou SIREN du bailleur est obligatoire",
            "max_length": "Le SIRET ou SIREN ne doivent pas excéder 14 caractères",
            "min_length": "Le SIRET ou SIREN doivent avoir 9 caractères minimum",
        },
    )
    capital_social = forms.FloatField(
        required=False,
    )
    adresse, code_postal, ville = forms_utils.address_form_fields()
    dg_nom = forms.CharField(
        max_length=255,
        error_messages={
            "required": "Le nom du signataire de la convention est obligatoire",
            "max_length": "Le nom du signataire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )
    dg_fonction = forms.CharField(
        max_length=255,
        error_messages={
            "required": "La fonction du signataire de la convention est obligatoire",
            "max_length": "La fonction du signataire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )
    dg_date_deliberation = forms.DateField(
        error_messages={
            "required": "La date de délibération est obligatoire",
        },
        help_text=(
            "Date à laquelle le signataire a reçu le mandat lui "
            + "permettant de signer la convention"
        ),
    )

    def clean_nom(self):
        nom = self.cleaned_data["nom"]
        return nom
