from django import forms


class ProgrammeNumberForm(forms.Form):
    numero_operation = forms.CharField(
        label="N° de décision de financement",
        required=False,
        max_length=255,
        error_messages={
            "max_length": "Le numero d'opération ne doit pas excéder 255 caractères",
        },
    )
