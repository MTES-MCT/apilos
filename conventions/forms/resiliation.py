from django import forms


class ConventionResiliationForm(forms.Form):

    date_resiliation = forms.DateField(
        required=True,
        label="Spécifier la date de résiliation/dénonciation",
        error_messages={
            "required": "Vous devez saisir une date de résiliation",
        },
    )
