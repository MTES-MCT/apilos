from django import forms

from programmes.models import NatureLogement


class LoyerSimulateurForm(forms.Form):

    nature_logement = forms.ChoiceField(
        label="Nature du logement",
        choices=NatureLogement.choices,
    )
    montant = forms.DecimalField(
        label="Loyer actuel",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer est obligatoire",
            "max_digits": "La loyer doit-être inférieur à 10000 €",
        },
    )
    date_initiale = forms.DateField(
        label="Date initiale",
        error_messages={
            "required": "La date initiale est obligatoire",
        },
    )
    date_actualisation = forms.DateField(
        label="Date d'actualisation",
        error_messages={
            "required": "La date initiale est obligatoire",
        },
    )
