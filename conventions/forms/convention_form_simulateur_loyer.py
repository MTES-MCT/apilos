from django import forms

from programmes.models import NatureLogement


class LoyerSimulateurForm(forms.Form):

    nature_logement = forms.ChoiceField(
        label="Nature du logement",
        choices=[
            e
            for e in NatureLogement.choices
            if e[0] in NatureLogement.eligible_for_update()
        ],
    )
    montant = forms.DecimalField(
        label="Loyer initial",
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
