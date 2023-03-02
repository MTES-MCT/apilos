from django import forms


class ConventionDateForm(forms.Form):

    televersement_convention_signee_le = forms.DateField(
        required=True,
        label="Indiquez la date de signature.",
        error_messages={
            "required": "Vous devez saisir une date de signature",
        },
    )
