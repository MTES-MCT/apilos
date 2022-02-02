from django import forms


class AdministrationForm(forms.Form):

    nom = forms.CharField(
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom de l'administration est obligatoire",
            "min_length": "Le nom de l'administration est obligatoire",
            "max_length": "Le nom de l'administration ne doit pas excéder 255 caractères",
        },
    )

    code = forms.CharField(
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le code de l'administration est obligatoire",
            "min_length": "Le code de l'administration est obligatoire",
            "max_length": "Le code de l'administration ne doit pas excéder 255 caractères",
        },
    )

    ville_signature = forms.CharField(
        required=False,
        max_length=255,
        error_messages={
            "max_length": "La ville de signature ne doit pas excéder 255 caractères",
        },
    )
