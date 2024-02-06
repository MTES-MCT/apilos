from django import forms


class ConventionDateSignatureForm(forms.Form):
    televersement_convention_signee_le = forms.DateField(
        required=True,
        label="Indiquez la date de signature.",
        error_messages={
            "required": "Vous devez saisir une date de signature",
        },
    )


class ConventionDateResiliationForm(forms.Form):
    date_resiliation = forms.DateField(
        required=True,
        label="Indiquez la date de résiliation.",
        error_messages={
            "required": "Vous devez saisir une date de résiliation",
        },
    )
